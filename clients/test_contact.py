# test_contact.py
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
    SUPER_EMAIL    = 'admin@example.com'
    SUPER_PASSWORD = 'adminpass'

    USER_EMAIL     = 'nono@example.com'
    USER_PASSWORD  = 'pass1234'

    # ── ログイン ──────────────────────────
    print_section('superuserログイン')
    super_token = fetch_token(SUPER_EMAIL, SUPER_PASSWORD)
    print('トークン取得成功' if super_token else 'ログイン失敗')

    # ── 問い合わせ送信（認証不要）────────
    print_section('問い合わせ送信（認証不要）')
    res = requests.post(f'{BASE_URL}api/contact/', json={
        'name':    'テストユーザー',
        'email':   'test@example.com',
        'subject': 'テストのお問い合わせ',
        'body':    'これはテストのお問い合わせです。\nよろしくお願いします。',
    })
    logger.debug({'send_contact status': res.status_code})
    print(res.json())
    contact_id = res.json().get('id') if res.status_code == 201 else None

    # ── 一般ユーザーは一覧取得不可 ────────
    print_section('一般ユーザーによる一覧取得（403確認）')
    user_token = fetch_token(USER_EMAIL, USER_PASSWORD)
    res = requests.get(
        f'{BASE_URL}api/contact/list/',
        headers=auth_headers(user_token),
    )
    logger.debug({'list_contact status': res.status_code})
    print(f'  ステータス: {res.status_code}')  # 403

    # ── 管理者による一覧取得 ──────────────
    print_section('管理者による一覧取得')
    res = requests.get(
        f'{BASE_URL}api/contact/list/',
        headers=auth_headers(super_token),
    )
    logger.debug({'list_contact status': res.status_code})
    for msg in res.json():
        print(f"  [{msg['id']}] {msg['subject']}"
              f" | {msg['name']} <{msg['email']}>"
              f" | 既読:{msg['is_read']}"
              f" | {msg['created_at']}")
    if res.json():
        contact_id = res.json()[0]['id']

    # ── 管理者による詳細取得 ──────────────
    print_section(f'詳細取得（id={contact_id}）')
    res = requests.get(
        f'{BASE_URL}api/contact/{contact_id}/',
        headers=auth_headers(super_token),
    )
    print(res.json())

    # ── 既読更新 ─────────────────────────
    print_section(f'既読更新（id={contact_id}）')
    res = requests.patch(
        f'{BASE_URL}api/contact/{contact_id}/',
        json={'is_read': True},
        headers=auth_headers(super_token),
    )
    logger.debug({'update_contact status': res.status_code})
    print(f"  is_read: {res.json().get('is_read')}")  # True

    # ── 削除 ─────────────────────────────
    print_section(f'削除（id={contact_id}）')
    res = requests.delete(
        f'{BASE_URL}api/contact/{contact_id}/',
        headers=auth_headers(super_token),
    )
    logger.debug({'delete_contact status': res.status_code})
    print(f'  削除ステータス: {res.status_code}')  # 204

    # ── 削除後の一覧確認 ──────────────────
    print_section('削除後の一覧')
    res = requests.get(
        f'{BASE_URL}api/contact/list/',
        headers=auth_headers(super_token),
    )
    print(f'  件数: {len(res.json())}件')