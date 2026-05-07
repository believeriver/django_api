# clients/test_screening.py
import requests
import json

BASE_URL = 'http://127.0.0.1:8000/'


def print_section(title):
    print(f'\n{"=" * 10} {title} {"=" * 10}')


if __name__ == '__main__':

    # ── スコア順 ──────────────────────────
    print_section('スクリーニング（スコア順）')
    res = requests.post(f'{BASE_URL}api/market/screening/', json={
        'eps_no_negative':      True,
        'dividend_no_zero':     True,
        'operating_margin_min': 8.0,
        'equity_ratio_min':     40.0,
        'sort_by':              'score',
    })
    data = res.json()
    print(f'該当銘柄数: {data["count"]}件')
    for r in data['results'][:10]:
        print(
            f"  [{r['code']}] {r['name'][:20]:<20} "
            f"スコア:{r['score']:3d} "
            f"配当利回り:{r['dividend']}% "
            f"分析年数:{r['years_analyzed']}年 "
            f"営業利益率:{r['details'].get('operating_margin_val')}% "
            f"自己資本比率:{r['details'].get('equity_ratio_val')}%"
        )

    # ── 配当利回り順 ──────────────────────
    print_section('スクリーニング（配当利回り順）')
    res = requests.post(f'{BASE_URL}api/market/screening/', json={
        'eps_no_negative':      True,
        'dividend_no_zero':     True,
        'operating_margin_min': 8.0,
        'equity_ratio_min':     40.0,
        'sort_by':              'dividend',
    })
    data = res.json()
    print(f'該当銘柄数: {data["count"]}件')
    for r in data['results'][:10]:
        print(
            f"  [{r['code']}] {r['name'][:20]:<20} "
            f"配当利回り:{r['dividend']}% "
            f"スコア:{r['score']:3d} "
            f"営業利益率:{r['details'].get('operating_margin_val')}%"
        )

    # ── 条件なし（全銘柄対象）────────────
    print_section('スクリーニング（条件なし・スコア順）')
    res = requests.post(f'{BASE_URL}api/market/screening/', json={
        'eps_no_negative':  True,
        'dividend_no_zero': True,
        'sort_by':          'score',
    })
    data = res.json()
    print(f'該当銘柄数: {data["count"]}件')
    for r in data['results'][:5]:
        print(
            f"  [{r['code']}] {r['name'][:20]:<20} "
            f"スコア:{r['score']:3d} "
            f"配当利回り:{r['dividend']}%"
        )