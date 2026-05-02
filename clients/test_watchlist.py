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
    EMAIL = 'testuser@example.com'
    PASSWORD = 'testuser'

    # ── ログイン ──────────────────────────
    print_section('ログイン')
    token = fetch_token(EMAIL, PASSWORD)
    print('トークン取得成功' if token else 'ログイン失敗')

    # ── ウォッチリスト作成 ────────────────
    print_section('ウォッチリスト作成')
    res = requests.post(f'{BASE_URL}api/watchlist/', json={
        'name': '高配当株ウォッチ',
        'memo': '長期保有候補',
    }, headers=auth_headers(token))
    print(res.status_code, res.json())
    watchlist_id = res.json().get('id')

    print_section('ウォッチリスト作成②')
    res = requests.post(f'{BASE_URL}api/watchlist/', json={
        'name': '成長株ウォッチ',
        'memo': '中期保有候補',
    }, headers=auth_headers(token))
    print(res.status_code, res.json())

    # ── ウォッチリスト一覧 ────────────────
    print_section('ウォッチリスト一覧')
    res = requests.get(f'{BASE_URL}api/watchlist/',
                       headers=auth_headers(token))
    for w in res.json():
        print(f"  [{w['id']}] {w['name']} "
              f"銘柄数:{w['item_count']} "
              f"アラート:{w['alert_count']}")

    # ── アイテム追加 ──────────────────────
    print_section('アイテム追加')
    res = requests.post(
        f'{BASE_URL}api/watchlist/{watchlist_id}/items/',
        json={
            'company_code_input': '8708',
            'target_price': 500.0,
            'memo': '高配当銘柄',
        },
        headers=auth_headers(token),
    )
    print(res.status_code, res.json())
    item_id = res.json().get('id')

    res = requests.post(
        f'{BASE_URL}api/watchlist/{watchlist_id}/items/',
        json={
            'company_code_input': '8614',
            'target_price': 300.0,
            'memo': '東洋証券',
        },
        headers=auth_headers(token),
    )
    print(res.status_code, res.json())

    # ── アイテム一覧 ──────────────────────
    print_section('アイテム一覧')
    res = requests.get(
        f'{BASE_URL}api/watchlist/{watchlist_id}/items/',
        headers=auth_headers(token),
    )
    for item in res.json():
        print(f"  [{item['company_code']}] {item['company_name']} "
              f"目標:{item['target_price']} "
              f"現在:{item['current_price']} "
              f"差分:{item['price_diff_pct']}% "
              f"アラート:{item['alert_label']}")

    # ── 株価自動更新・アラート判定 ──────────
    print_section('株価自動更新（最高値含む）')
    res = requests.post(
        f'{BASE_URL}api/watchlist/{watchlist_id}/items/refresh/',
        headers=auth_headers(token),
    )
    print('updated:', res.json().get('updated'))
    print('errors: ', res.json().get('errors'))
    for item in res.json().get('watchlist', {}).get('items', []):
        print(f"  [{item['company_code']}] {item['company_name']}")
        print(f"    現在株価  : {item['current_price']}")
        print(f"    目標株価  : {item['target_price']}")
        print(f"    目標差分  : {item['price_diff_pct']}% → {item['alert_label']}")
        print(f"    1年最高値 : {item['high_price_1y']} ({item['high_price_1y_at']})")
        print(f"    最高値差分: {item['high_diff_pct']}% → {item['high_alert_label']}")

    # ── 手動で current_price を更新 ────────
    print_section(f'手動で current_price を更新（id={item_id}）')
    res = requests.patch(
        f'{BASE_URL}api/watchlist/{watchlist_id}/items/{item_id}/',
        json={'current_price': 400.0},
        headers=auth_headers(token),
    )
    print(res.status_code)
    item = res.json()
    print(f"  現在:{item['current_price']} "
          f"目標差分:{item['price_diff_pct']}% ({item['alert_label']}) "
          f"最高値差分:{item['high_diff_pct']}% ({item['high_alert_label']})")

    # ── target_price を更新してアラート再判定 ──
    print_section(f'target_price を更新（id={item_id}）')
    res = requests.patch(
        f'{BASE_URL}api/watchlist/{watchlist_id}/items/{item_id}/',
        json={'target_price': 1600.0},
        headers=auth_headers(token),
    )
    print(res.status_code)
    item = res.json()
    print(f"  目標:{item['target_price']} "
          f"現在:{item['current_price']} "
          f"目標差分:{item['price_diff_pct']}% ({item['alert_label']})")

    # ── ウォッチリスト詳細 ────────────────
    print_section('ウォッチリスト詳細')
    res = requests.get(
        f'{BASE_URL}api/watchlist/{watchlist_id}/',
        headers=auth_headers(token),
    )
    print(f"  名前: {res.json()['name']}")
    print(f"  銘柄数: {res.json()['item_count']}")

    # ── ウォッチリスト更新 ────────────────
    print_section('ウォッチリスト更新')
    res = requests.patch(
        f'{BASE_URL}api/watchlist/{watchlist_id}/',
        json={'name': '高配当株ウォッチ（更新）'},
        headers=auth_headers(token),
    )
    print(res.status_code, res.json().get('name'))

    # ── アイテム削除 ──────────────────────
    print_section(f'アイテム削除（id={item_id}）')
    res = requests.delete(
        f'{BASE_URL}api/watchlist/{watchlist_id}/items/{item_id}/',
        headers=auth_headers(token),
    )
    print('削除ステータス:', res.status_code)

    # ── 認証なしアクセス（401確認）────────
    print_section('認証なしアクセス（401確認）')
    res = requests.get(f'{BASE_URL}api/watchlist/')
    print('ステータス:', res.status_code)