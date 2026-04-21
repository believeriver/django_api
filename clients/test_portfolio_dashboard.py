# test_portfolio.py
import requests
import logging
import sys

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger(__name__)

BASE_URL = 'http://127.0.0.1:8000/'


# ─────────────────────────────────────────
# 認証
# ─────────────────────────────────────────

def fetch_token(_email: str, _password: str):
    _url = f'{BASE_URL}api/auth/login/'
    response = requests.post(_url, json={
        'email':    _email,
        'password': _password,
    })
    logger.debug({'fetch_token status': response.status_code})
    if response.status_code != 200:
        logger.error({'fetch_token error': response.json()})
        return None
    return response.json().get('access')


def auth_headers(_token: str) -> dict:
    return {'Authorization': f'Bearer {_token}'}


# ─────────────────────────────────────────
# ポートフォリオ操作
# ─────────────────────────────────────────

def get_portfolio(_token: str) -> list:
    _url = f'{BASE_URL}api/portfolio/'
    response = requests.get(_url, headers=auth_headers(_token))
    logger.debug({'get_portfolio status': response.status_code})
    return response.json()


def add_portfolio(_token: str, _company_code: str, _shares: int,
                  _purchase_price: str, _purchased_at: str, _memo: str = '') -> dict:
    _url = f'{BASE_URL}api/portfolio/'
    response = requests.post(_url, json={
        'company_code':   _company_code,
        'shares':         _shares,
        'purchase_price': _purchase_price,
        'purchased_at':   _purchased_at,
        'memo':           _memo,
    }, headers=auth_headers(_token))
    logger.debug({'add_portfolio status': response.status_code})
    return response.json()


def get_portfolio_detail(_token: str, _id: int) -> dict:
    _url = f'{BASE_URL}api/portfolio/{_id}/'
    response = requests.get(_url, headers=auth_headers(_token))
    logger.debug({'get_portfolio_detail status': response.status_code})
    return response.json()


def update_portfolio(_token: str, _id: int, **kwargs) -> dict:
    _url = f'{BASE_URL}api/portfolio/{_id}/'
    response = requests.patch(_url, json=kwargs, headers=auth_headers(_token))
    logger.debug({'update_portfolio status': response.status_code})
    return response.json()


def delete_portfolio(_token: str, _id: int) -> int:
    _url = f'{BASE_URL}api/portfolio/{_id}/'
    response = requests.delete(_url, headers=auth_headers(_token))
    logger.debug({'delete_portfolio status': response.status_code})
    return response.status_code


# ─────────────────────────────────────────
# ダッシュボード・集計
# ─────────────────────────────────────────

def get_dashboard(_token: str) -> list:
    """ダッシュボード用（業種・指標込み）"""
    _url = f'{BASE_URL}api/portfolio/dashboard/'
    response = requests.get(_url, headers=auth_headers(_token))
    logger.debug({'get_dashboard status': response.status_code})
    return response.json()


def get_industry(_token: str) -> list:
    """業種別集計（円グラフ用）"""
    _url = f'{BASE_URL}api/portfolio/industry/'
    response = requests.get(_url, headers=auth_headers(_token))
    logger.debug({'get_industry status': response.status_code})
    return response.json()


# ─────────────────────────────────────────
# 表示ヘルパー
# ─────────────────────────────────────────

def print_section(title: str):
    print(f'\n{"=" * 10} {title} {"=" * 10}')


def print_portfolio_list(data: list):
    for item in data:
        print(f"  [{item['company_code']}] {item['company_name']}"
              f" | 合計:{item['total_shares']}株"
              f" | 平均単価:{item['avg_purchase_price']}"
              f" | 履歴:{len(item['records'])}件")


def print_dashboard(data: list):
    total_dividend_income = 0

    for item in data:
        per             = item.get('per')
        pbr             = item.get('pbr')
        dividend_income = item.get('dividend_income', 0)
        source          = item.get('dividend_income_source')
        total_dividend_income += dividend_income

        # 計算根拠の表示
        if source == 'dividend_per_share':
            source_label = '1株配当ベース'
        elif source == 'dividend_yield':
            source_label = '利回りベース（概算）'
        else:
            source_label = 'データなし'

        print(
            f"  [{item['company_code']}] {item['company_name']}"
            f" | 業種:{item.get('industry', '未分類')}"
            f" | PER:{per if per is not None else '-'}"
            f" | PBR:{pbr if pbr is not None else '-'}"
            f" | 合計:{item['total_shares']}株"
            f" | 平均単価:{item['avg_purchase_price']:>10,.0f}円"
            f" | 配当利回り:{item.get('dividend_yield') or '-'}%"
            f" | 1株配当:{item.get('dividend_per_share') or '-'}円"
            f" | 配当収入予想:{dividend_income:>10,.0f}円"
            f" | ({source_label})"
        )

    print(f"\n  {'─' * 60}")
    print(f"  年間配当収入予想合計: {total_dividend_income:>12,.0f}円")
    print(f"  ※利回りベースの銘柄は取得単価基準のため概算値です")

def print_industry(data: list):
    for item in data:
        print(f"  {item['industry']:12}"
              f" | 投資額:{item['total_cost']:>12,.0f}円"
              f" | 比率:{item['ratio']}%")


# ─────────────────────────────────────────
# メイン
# ─────────────────────────────────────────

if __name__ == '__main__':
    EMAIL    = 'testuser@example.com'
    PASSWORD = 'testuser'

    # ── ログイン ──────────────────────────
    print_section('ログイン')
    token = fetch_token(EMAIL, PASSWORD)
    if not token:
        print('ログイン失敗。終了します。')
        sys.exit(1)
    print('トークン取得成功')

    # ── 銘柄追加 ─────────────────────────
    print_section('銘柄追加（7203 1回目）')
    res = add_portfolio(token, '7203', 100, '2000.00', '2025-01-10', '初回購入')
    print(res)
    record_id_1 = res.get('id')

    print_section('銘柄追加（7203 2回目）')
    res = add_portfolio(token, '7203', 200, '2225.00', '2025-06-01')
    print(res)
    record_id_2 = res.get('id')

    print_section('銘柄追加（8963）')
    res = add_portfolio(token, '8963', 50, '1500.00', '2025-03-15', 'J-REIT')
    print(res)

    # ── 一覧取得 ─────────────────────────
    print_section('ポートフォリオ一覧')
    print_portfolio_list(get_portfolio(token))

    # ── ダッシュボード ────────────────────
    print_section('ダッシュボード（業種・指標込み）')
    dashboard = get_dashboard(token)
    if isinstance(dashboard, list):
        print_dashboard(dashboard)
    else:
        print('エラー:', dashboard)

    # ── 業種別集計 ────────────────────────
    print_section('業種別集計（円グラフ用）')
    industry = get_industry(token)
    if isinstance(industry, list):
        print_industry(industry)
    else:
        print('エラー:', industry)

    # ── 1件更新 ───────────────────────────
    print_section(f'更新（id={record_id_1} メモ変更）')
    print(update_portfolio(token, record_id_1, memo='ナンピン買い'))

    # ── 1件削除 ───────────────────────────
    print_section(f'削除（id={record_id_2}）')
    print(f'削除ステータス: {delete_portfolio(token, record_id_2)}')

    # ── 削除後の一覧確認 ──────────────────
    print_section('削除後のポートフォリオ一覧')
    print_portfolio_list(get_portfolio(token))
