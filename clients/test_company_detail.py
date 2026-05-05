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
    EMAIL    = 'admin@email.com'
    PASSWORD = 'adminpass'

    # ── ログイン ──────────────────────────
    print_section('ログイン')
    token = fetch_token(EMAIL, PASSWORD)
    print('トークン取得成功' if token else 'ログイン失敗')

    # ── 企業詳細情報の取得（Claude API） ──
    print_section('企業詳細情報取得（9986 蔵王産業）')
    res = requests.post(
        f'{BASE_URL}api/market/companies/9986/fetch-detail/',
        headers=auth_headers(token),
    )
    print('ステータス:', res.status_code)
    if res.status_code == 201:
        data = res.json()
        print(f"  企業名  : {data['name']}")
        print(f"  概要    : {data['summary']}")
        print(f"  事業内容: {data['business']}")
        print(f"  特徴    : {data['feature']}")
        print(f"  リスク  : {data['risk']}")
        print(f"  取得日時: {data['fetched_at']}")
    else:
        print('エラー:', res.json())

    # ── 保存済み詳細情報の取得 ────────────
    print_section('保存済み詳細情報の取得（認証不要）')
    res = requests.get(
        f'{BASE_URL}api/market/companies/9986/detail/',
    )
    print('ステータス:', res.status_code)
    if res.status_code == 200:
        data = res.json()
        print(f"  企業名  : {data['name']}")
        print(f"  概要    : {data['summary']}")
        print(f"  事業内容: {data['business']}")
        print(f"  特徴    : {data['feature']}")
        print(f"  リスク  : {data['risk']}")
        print(f"  公式サイト: {data.get('website', 'なし')}")
        print(f"  Wiki URL  : {data.get('wiki_url', 'なし')}")
        print(f"  取得日時: {data['fetched_at']}")
    else:
        print('エラー:', res.json())

    # ── 未取得の企業（404確認）────────────
    print_section('未取得企業の詳細情報（404確認）')
    res = requests.get(
        f'{BASE_URL}api/market/companies/8614/detail/',
    )
    print('ステータス:', res.status_code)
    print(res.json())

    # ── 認証なしで fetch-detail（401確認）─
    print_section('認証なしで fetch-detail（401確認）')
    res = requests.post(
        f'{BASE_URL}api/market/companies/9986/fetch-detail/',
    )
    print('ステータス:', res.status_code)

    # ── 存在しない銘柄コード（404確認）────
    print_section('存在しない銘柄コード（404確認）')
    res = requests.post(
        f'{BASE_URL}api/market/companies/9999/fetch-detail/',
        headers=auth_headers(token),
    )
    print('ステータス:', res.status_code)
    print(res.json())