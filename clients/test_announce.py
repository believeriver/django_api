# test_announce.py
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
    SUPER_EMAIL    = 'nobuyuki.galois@gmail.com'
    SUPER_PASSWORD = ''

    # ── ログイン ──────────────────────────
    print_section('superuserログイン')
    token = fetch_token(SUPER_EMAIL, SUPER_PASSWORD)
    print('トークン取得成功' if token else 'ログイン失敗')

    # ── お知らせ作成 ──────────────────────
    print_section('お知らせ作成（メンテナンス）')
    res = requests.post(f'{BASE_URL}api/announce/', json={
        'title':   'システムメンテナンスのお知らせ',
        'content': '## メンテナンス\n\n2026年5月1日 0:00〜6:00 メンテナンスを実施します。',
        'type':    'maintenance',
        'status':  'published',
        'is_pinned': True,
    }, headers=auth_headers(token))
    logger.debug({'create status': res.status_code})
    print(res.json())
    announce_id = res.json().get('id')

    print_section('お知らせ作成（新機能）')
    res = requests.post(f'{BASE_URL}api/announce/', json={
        'title':   'お知らせ・変更管理機能を追加しました',
        'content': '## 新機能\n\nお知らせと変更履歴の管理機能を追加しました。',
        'type':    'feature',
        'status':  'published',
        'is_pinned': False,
    }, headers=auth_headers(token))
    print(res.json())

    # ── お知らせ一覧（認証不要）──────────
    print_section('お知らせ一覧（認証不要）')
    res = requests.get(f'{BASE_URL}api/announce/')
    for a in res.json():
        print(f"  [{a['type_label']}] {a['title']}"
              f" | ピン:{a['is_pinned']}"
              f" | 表示中:{a['is_active']}")

    # ── タイプフィルタ ────────────────────
    print_section('メンテナンスのみ絞り込み')
    res = requests.get(f'{BASE_URL}api/announce/?type=maintenance')
    print(f'  件数: {len(res.json())}件')

    # ── 管理者：全件取得 ──────────────────
    print_section('管理者：全件取得（下書き含む）')
    res = requests.get(
        f'{BASE_URL}api/announce/?all=true',
        headers=auth_headers(token),
    )
    print(f'  件数: {len(res.json())}件')

    # ── お知らせ更新 ──────────────────────
    print_section(f'お知らせ更新（id={announce_id}）')
    res = requests.patch(
        f'{BASE_URL}api/announce/{announce_id}/',
        json={'status': 'archived'},
        headers=auth_headers(token),
    )
    print(f"  status: {res.json().get('status')}")

    # ── 変更履歴作成 ──────────────────────
    print_section('変更履歴作成')
    res = requests.post(f'{BASE_URL}api/announce/changelog/', json={
        'version':     'v1.1.0',
        'type':        'feature',
        'title':       'お知らせ・変更管理機能を追加',
        'content':     '## 追加内容\n\n- お知らせAPI\n- 変更履歴API\n- 表示期間制御',
        'released_at': '2026-04-26T00:00:00+09:00',
    }, headers=auth_headers(token))
    logger.debug({'changelog create status': res.status_code})
    print(res.json())
    changelog_id = res.json().get('id')

    res = requests.post(f'{BASE_URL}api/announce/changelog/', json={
        'version':     'v1.0.0',
        'type':        'infra',
        'title':       'VPSサーバーへのデプロイ',
        'content':     '## インフラ\n\n- Rocky Linux 9.4\n- Docker Compose\n- Let\'s Encrypt SSL',
        'released_at': '2026-04-24T00:00:00+09:00',
    }, headers=auth_headers(token))
    print(res.json())

    # ── 変更履歴一覧（認証不要）──────────
    print_section('変更履歴一覧（認証不要）')
    res = requests.get(f'{BASE_URL}api/announce/changelog/')
    for c in res.json():
        print(f"  [{c['version']}] [{c['type_label']}] {c['title']}")

    # ── バージョン絞り込み ────────────────
    print_section('v1.0.0 の変更履歴')
    res = requests.get(f'{BASE_URL}api/announce/changelog/?version=v1.0.0')
    print(f'  件数: {len(res.json())}件')

    # ── 変更履歴削除 ──────────────────────
    print_section(f'変更履歴削除（id={changelog_id}）')
    res = requests.delete(
        f'{BASE_URL}api/announce/changelog/{changelog_id}/',
        headers=auth_headers(token),
    )
    print(f'  削除ステータス: {res.status_code}')

    # ── 一般ユーザーの作成試行（403確認）──
    print_section('一般ユーザーによる作成（403確認）')
    res = requests.post(f'{BASE_URL}api/announce/', json={
        'title': 'テスト', 'content': 'テスト', 'type': 'info',
    })
    print(f'  ステータス: {res.status_code}')  # 401
