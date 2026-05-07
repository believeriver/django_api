# api_market/screening.py
from django.db.models import Prefetch
from .models import Company, Financial
import re


def to_float(value) -> float or None:
    """sales（CharField）を数値に変換"""
    if value is None:
        return None
    try:
        # カンマ・スペース・単位（百万円等）を除去
        cleaned = re.sub(r'[^\d.-]', '', str(value))
        return float(cleaned) if cleaned else None
    except (ValueError, TypeError):
        return None


def analyze_company(financials: list) -> dict:
    """
    企業の財務データを分析してスコアと詳細を返す

    financials: fiscal_year 昇順のFinancialリスト
    """
    if not financials:
        return None

    n     = len(financials)
    score = 0
    details = {}

    # ── 各年のデータを抽出 ────────────────
    sales_list   = [to_float(f.sales)           for f in financials]
    margin_list  = [f.operating_margin           for f in financials]
    eps_list     = [f.eps                        for f in financials]
    equity_list  = [f.equity_ratio               for f in financials]
    cf_list      = [f.operating_cash_flow        for f in financials]
    cash_list    = [f.cash_and_equivalents       for f in financials]
    div_list     = [f.dividend_per_share         for f in financials]
    payout_list  = [f.payout_ratio               for f in financials]

    latest = financials[-1]

    # ── 売上高の分析 ──────────────────────
    valid_sales = [s for s in sales_list if s is not None]
    if len(valid_sales) >= 2:
        # 右肩上がり（単調増加）
        sales_trend = all(
            valid_sales[i] <= valid_sales[i+1]
            for i in range(len(valid_sales)-1)
        )
        # ブレが小さい（標準偏差/平均 < 0.2）
        import statistics
        mean = statistics.mean(valid_sales)
        if mean > 0:
            std  = statistics.stdev(valid_sales) if len(valid_sales) > 1 else 0
            sales_stable = (std / mean) < 0.2
        else:
            sales_stable = False

        if sales_trend:
            score += 10
        if sales_stable:
            score += 5
        details['sales_growth']  = sales_trend
        details['sales_stable']  = sales_stable
    else:
        details['sales_growth'] = None
        details['sales_stable'] = None

    # ── 営業利益率の分析 ──────────────────
    valid_margin = [m for m in margin_list if m is not None]
    if valid_margin:
        latest_margin = valid_margin[-1]
        margin_8  = latest_margin >= 8.0
        margin_10 = latest_margin >= 10.0
        if margin_8:
            score += 10
        if margin_10:
            score += 5
        details['operating_margin_ok']  = margin_8
        details['operating_margin_10']  = margin_10
        details['operating_margin_val'] = latest_margin
    else:
        details['operating_margin_ok']  = None
        details['operating_margin_10']  = None
        details['operating_margin_val'] = None

    # ── EPS の分析 ────────────────────────
    valid_eps = [e for e in eps_list if e is not None]
    if valid_eps:
        eps_no_negative = all(e >= 0 for e in valid_eps)
        eps_growth      = all(
            valid_eps[i] <= valid_eps[i+1]
            for i in range(len(valid_eps)-1)
        ) if len(valid_eps) >= 2 else None

        if eps_no_negative:
            score += 10
        if eps_growth:
            score += 10

        details['eps_no_negative'] = eps_no_negative
        details['eps_growth']      = eps_growth
        details['eps_val']         = valid_eps[-1]
    else:
        details['eps_no_negative'] = None
        details['eps_growth']      = None
        details['eps_val']         = None

    # ── 自己資本比率の分析 ────────────────
    valid_equity = [e for e in equity_list if e is not None]
    if valid_equity:
        latest_equity = valid_equity[-1]
        equity_40 = latest_equity >= 40.0
        equity_60 = latest_equity >= 60.0
        equity_80 = latest_equity >= 80.0

        if equity_40:
            score += 10
        if equity_60:
            score += 5
        if equity_80:
            score += 5

        details['equity_ratio_40']  = equity_40
        details['equity_ratio_60']  = equity_60
        details['equity_ratio_80']  = equity_80
        details['equity_ratio_val'] = latest_equity
    else:
        details['equity_ratio_40']  = None
        details['equity_ratio_60']  = None
        details['equity_ratio_80']  = None
        details['equity_ratio_val'] = None

    # ── 営業CF の分析 ─────────────────────
    valid_cf = [c for c in cf_list if c is not None]
    if valid_cf:
        cf_positive = all(c > 0 for c in valid_cf)
        cf_growth   = all(
            valid_cf[i] <= valid_cf[i+1]
            for i in range(len(valid_cf)-1)
        ) if len(valid_cf) >= 2 else None

        if cf_positive:
            score += 10
        if cf_growth:
            score += 5

        details['cf_positive'] = cf_positive
        details['cf_growth']   = cf_growth
        details['cf_val']      = valid_cf[-1]
    else:
        details['cf_positive'] = None
        details['cf_growth']   = None
        details['cf_val']      = None

    # ── 現金等の分析 ──────────────────────
    valid_cash = [c for c in cash_list if c is not None]
    if len(valid_cash) >= 2:
        cash_growth = valid_cash[-1] > valid_cash[0]
        if cash_growth:
            score += 5
        details['cash_growth'] = cash_growth
        details['cash_val']    = valid_cash[-1]
    else:
        details['cash_growth'] = None
        details['cash_val']    = valid_cash[-1] if valid_cash else None

    # ── 一株配当の分析 ────────────────────
    valid_div = [d for d in div_list if d is not None]
    if valid_div:
        div_no_zero = all(d > 0 for d in valid_div)
        div_growth  = all(
            valid_div[i] <= valid_div[i+1]
            for i in range(len(valid_div)-1)
        ) if len(valid_div) >= 2 else None

        if div_no_zero:
            score += 10
        if div_growth:
            score += 5

        details['dividend_stable'] = div_no_zero
        details['dividend_growth'] = div_growth
        details['dividend_val']    = valid_div[-1]
    else:
        details['dividend_stable'] = None
        details['dividend_growth'] = None
        details['dividend_val']    = None

    # ── 配当性向の分析 ────────────────────
    valid_payout = [p for p in payout_list if p is not None]
    if valid_payout:
        latest_payout   = valid_payout[-1]
        payout_ok       = 30.0 <= latest_payout <= 50.0
        payout_high     = latest_payout > 80.0

        if payout_ok:
            score += 10

        details['payout_ratio_ok']  = payout_ok
        details['payout_ratio_high'] = payout_high
        details['payout_ratio_val'] = latest_payout
    else:
        details['payout_ratio_ok']   = None
        details['payout_ratio_high'] = None
        details['payout_ratio_val']  = None

    # ── 最新データ ────────────────────────
    latest_data = {
        'fiscal_year':         latest.fiscal_year,
        'sales':               to_float(latest.sales),
        'operating_margin':    latest.operating_margin,
        'eps':                 latest.eps,
        'equity_ratio':        latest.equity_ratio,
        'operating_cash_flow': latest.operating_cash_flow,
        'cash_and_equivalents': latest.cash_and_equivalents,
        'dividend_per_share':  latest.dividend_per_share,
        'payout_ratio':        latest.payout_ratio,
    }

    return {
        'score':          score,
        'years_analyzed': n,
        'details':        details,
        'latest':         latest_data,
    }


def run_screening(
    eps_no_negative: bool   = True,
    dividend_no_zero: bool  = True,
    operating_margin_min: float = None,
    equity_ratio_min: float = None,
    sort_by: str            = 'score',  # 'score' or 'dividend'
) -> list:
    """
    スクリーニングを実行して結果を返す

    sort_by: 'score' → スコア降順
             'dividend' → 配当利回り降順
    """
    # 全企業の財務データを取得
    companies = Company.objects.prefetch_related(
        Prefetch(
            'financials',
            queryset=Financial.objects.order_by('fiscal_year'),
            to_attr='financial_list',
        )
    ).select_related('information')

    results = []

    for company in companies:
        financials = company.financial_list
        if not financials:
            continue

        analysis = analyze_company(financials)
        if not analysis:
            continue

        details = analysis['details']

        # ── 必須フィルタ ──────────────────
        # EPSマイナス除外
        if eps_no_negative and details.get('eps_no_negative') is False:
            continue

        # 無配除外
        if dividend_no_zero and details.get('dividend_stable') is False:
            continue

        # 営業利益率の最低条件
        if operating_margin_min is not None:
            val = details.get('operating_margin_val')
            if val is None or val < operating_margin_min:
                continue

        # 自己資本比率の最低条件
        if equity_ratio_min is not None:
            val = details.get('equity_ratio_val')
            if val is None or val < equity_ratio_min:
                continue

        results.append({
            'code':           company.code,
            'name':           company.name,
            'dividend':       company.dividend,
            'score':          analysis['score'],
            'years_analyzed': analysis['years_analyzed'],
            'details':        analysis['details'],
            'latest':         analysis['latest'],
        })

    # ── ソート ────────────────────────────
    if sort_by == 'dividend':
        results.sort(
            key=lambda x: x['dividend'] if x['dividend'] is not None else 0,
            reverse=True,
        )
    else:
        results.sort(key=lambda x: x['score'], reverse=True)

    return results
