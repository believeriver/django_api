# clients/test_screening_db.py
import requests
import logging
import sys

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger(__name__)

BASE_URL = 'http://127.0.0.1:8000/'


def fetch_token(_email, _password):
    response = requests.post(f'{BASE_URL}api/auth/login/', json={
        'email': _email, 'password': _password,
    })
    return response.json().get('access')


def auth_headers(_token):
    return {'Authorization': f'Bearer {_token}'}


def print_section(title):
    print(f'\n{"=" * 10} {title} {"=" * 10}')


if __name__ == '__main__':
    EMAIL = 'admin@email.com'
    PASSWORD = 'adminpass'

    # ── ログイン ──────────────────────────
    print_section('ログイン')
    token = fetch_token(EMAIL, PASSWORD)
    print('トークン取得成功' if token else 'ログイン失敗')

    # ── 更新前にGET（空のはず）────────────
    print_section('更新前にGET（空のはず）')
    res = requests.get(f'{BASE_URL}api/market/screening/')
    print(f'ステータス: {res.status_code}')
    print(f'件数: {res.json().get("count")}')
    print(f'更新日時: {res.json().get("refreshed_at")}')

    # ── スクリーニング更新（superuserのみ）─
    print_section('スクリーニング更新（superuser）')
    res = requests.post(
        f'{BASE_URL}api/market/screening/refresh/',
        headers=auth_headers(token),
    )
    print(f'ステータス: {res.status_code}')
    print(res.json())

    # ── DBからGET（スコア順）──────────────
    print_section('DBからGET（スコア順・デフォルト）')
    res = requests.get(
        f'{BASE_URL}api/market/screening/',
        params={
            'sort_by':              'score',
            'exclude_reit':         'false',
            'dividend_yield_min':   3.0,
            'equity_ratio_min':     40.0,
            'operating_margin_min': 8.0,
        }
    )
    print(f'ステータス: {res.status_code}')
    data = res.json()
    print(f'件数: {data["count"]}')
    print(f'更新日時: {data["refreshed_at"]}')
    for r in data['results'][:5]:
        print(
            f"  [{r['code']}] {r['name'][:20]:<20} "
            f"スコア:{r['score']:3d} "
            f"配当:{r['dividend']}% "
            f"分析年数:{r['years_analyzed']}年"
        )

    # ── DBからGET（配当利回り順）──────────
    print_section('DBからGET（配当利回り順・リート除外）')
    res = requests.get(
        f'{BASE_URL}api/market/screening/',
        params={
            'sort_by':              'dividend',
            'exclude_reit':         'true',
            'dividend_yield_min':   3.0,
            'equity_ratio_min':     40.0,
            'operating_margin_min': 8.0,
        }
    )
    data = res.json()
    print(f'件数: {data["count"]}')
    for r in data['results'][:5]:
        print(
            f"  [{r['code']}] {r['name'][:20]:<20} "
            f"配当:{r['dividend']}% "
            f"スコア:{r['score']:3d}"
        )

    # ── 認証なしで refresh（401確認）──────
    print_section('認証なしで refresh（401確認）')
    res = requests.post(f'{BASE_URL}api/market/screening/refresh/')
    print(f'ステータス: {res.status_code}')

    # ── min_years フィルタ ────────────────
    print_section('min_years=5 フィルタ')
    res = requests.get(
        f'{BASE_URL}api/market/screening/',
        params={
            'min_years':            5,
            'dividend_yield_min':   3.0,
            'operating_margin_min': 8.0,
            'equity_ratio_min':     40.0,
            'exclude_reit':         'true',
        }
    )
    data = res.json()
    print(f'件数: {data["count"]}')
    for r in data['results'][:5]:
        print(
            f"  [{r['code']}] {r['name'][:20]:<20} "
            f"スコア:{r['score']:3d} "
            f"分析年数:{r['years_analyzed']}年"
        )
