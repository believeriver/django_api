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
    """認証ヘッダーを返すヘルパー"""
    return {'Authorization': f'Bearer {_token}'}


# ─────────────────────────────────────────
# ポートフォリオ操作
# ─────────────────────────────────────────

def get_portfolio(_token: str) -> dict:
    """一覧取得（企業ごとに集計）"""
    _url = f'{BASE_URL}api/portfolio/'
    response = requests.get(_url, headers=auth_headers(_token))
    logger.debug({'get_portfolio status': response.status_code})
    return response.json()


def add_portfolio(_token: str, _company_code: str, _shares: int,
                  _purchase_price: str, _purchased_at: str, _memo: str = '') -> dict:
    """銘柄追加（購入履歴1件）"""
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
    """購入履歴1件取得"""
    _url = f'{BASE_URL}api/portfolio/{_id}/'
    response = requests.get(_url, headers=auth_headers(_token))
    logger.debug({'get_portfolio_detail status': response.status_code})
    return response.json()


def update_portfolio(_token: str, _id: int, **kwargs) -> dict:
    """購入履歴1件更新"""
    _url = f'{BASE_URL}api/portfolio/{_id}/'
    response = requests.patch(_url, json=kwargs, headers=auth_headers(_token))
    logger.debug({'update_portfolio status': response.status_code})
    return response.json()


def delete_portfolio(_token: str, _id: int) -> int:
    """購入履歴1件削除"""
    _url = f'{BASE_URL}api/portfolio/{_id}/'
    response = requests.delete(_url, headers=auth_headers(_token))
    logger.debug({'delete_portfolio status': response.status_code})
    return response.status_code


# ─────────────────────────────────────────
# メイン
# ─────────────────────────────────────────

if __name__ == '__main__':
    EMAIL    = 'testuser@example.com'
    PASSWORD = 'testuser'

    # ── ログイン ──────────────────────────
    print('\n===== ログイン =====')
    token = fetch_token(EMAIL, PASSWORD)
    if not token:
        print('ログイン失敗。終了します。')
        sys.exit(1)
    print('トークン取得成功')

    # ── 銘柄追加 ─────────────────────────
    print('\n===== 銘柄追加（7203 1回目）=====')
    res = add_portfolio(token, '7203', 100, '2000.00', '2025-01-10', '初回購入')
    print(res)
    record_id_1 = res.get('id')

    print('\n===== 銘柄追加（7203 2回目）=====')
    res = add_portfolio(token, '7203', 200, '2225.00', '2025-06-01')
    print(res)
    record_id_2 = res.get('id')

    print('\n===== 銘柄追加（8963）=====')
    res = add_portfolio(token, '8963', 50, '1500.00', '2025-03-15', 'J-REIT')
    print(res)

    # ── 一覧取得（集計済み）──────────────
    print('\n===== ポートフォリオ一覧（集計）=====')
    res = get_portfolio(token)
    for item in res:
        print(f"  {item['company_code']} {item['company_name']}"
              f" | 合計:{item['total_shares']}株"
              f" | 平均単価:{item['avg_purchase_price']}"
              f" | 履歴件数:{len(item['records'])}")

    # ── 1件取得 ───────────────────────────
    print(f'\n===== 詳細取得（id={record_id_1}）=====')
    print(get_portfolio_detail(token, record_id_1))

    # ── 1件更新 ───────────────────────────
    print(f'\n===== 更新（id={record_id_1} メモ変更）=====')
    print(update_portfolio(token, record_id_1, memo='ナンピン買い'))

    # ── 1件削除 ───────────────────────────
    print(f'\n===== 削除（id={record_id_2}）=====')
    status_code = delete_portfolio(token, record_id_2)
    print(f'削除ステータス: {status_code}')

    # ── 削除後の一覧確認 ──────────────────
    print('\n===== 削除後の一覧 =====')
    res = get_portfolio(token)
    for item in res:
        print(f"  {item['company_code']} {item['company_name']}"
              f" | 合計:{item['total_shares']}株"
              f" | 平均単価:{item['avg_purchase_price']}"
              f" | 履歴件数:{len(item['records'])}")
