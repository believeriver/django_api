# test_analytics.py
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
    # SUPER_EMAIL    = 'admin@example.com'
    # SUPER_PASSWORD = 'adminpass'
    SUPER_EMAIL = 'nobuyuki.galois@gmail.com'
    SUPER_PASSWORD = 'nobuyuki@12345'

    USER_EMAIL     = 'nono@example.com'
    USER_PASSWORD  = 'pass1234'

    # ── ログイン ──────────────────────────
    print_section('superuserログイン')
    super_token = fetch_token(SUPER_EMAIL, SUPER_PASSWORD)
    print('トークン取得成功' if super_token else 'ログイン失敗')

    # ── アクセスを発生させる ──────────────
    print_section('アクセスを発生させる')
    for _ in range(3):
        requests.get(f'{BASE_URL}api/blog/posts/')
    for _ in range(2):
        requests.get(f'{BASE_URL}api/techlog/posts/')
    requests.get(f'{BASE_URL}api/portfolio/', headers=auth_headers(super_token))
    print('アクセス完了')

    # ── サマリー ─────────────────────────
    print_section('サマリー')
    res = requests.get(
        f'{BASE_URL}api/analytics/summary/',
        headers=auth_headers(super_token),
    )
    data = res.json()
    print(f"  総アクセス数    : {data['access_logs']['total']}")
    print(f"  今日            : {data['access_logs']['today']}")
    print(f"  過去7日         : {data['access_logs']['last_7_days']}")
    print(f"  平均レスポンス  : {data['access_logs']['avg_response_ms']}ms")
    print(f"  サイト別        : {data['access_logs']['by_site']}")
    print(f"  ログイン成功30d : {data['security_logs']['login_success_30d']}")
    print(f"  ログイン失敗30d : {data['security_logs']['login_failed_30d']}")

    # ── アクセスログ一覧 ──────────────────
    print_section('アクセスログ一覧（直近10件）')
    res = requests.get(
        f'{BASE_URL}api/analytics/access-logs/?limit=10',
        headers=auth_headers(super_token),
    )
    for log in res.json():
        print(f"  [{log['site']}] {log['method']} {log['path']}"
              f" {log['status_code']} {log['response_time']}ms"
              f" {log['ip_address']}")

    # ── サイト別フィルタ ──────────────────
    print_section('blogのアクセスログ')
    res = requests.get(
        f'{BASE_URL}api/analytics/access-logs/?site=blog&limit=5',
        headers=auth_headers(super_token),
    )
    print(f'  件数: {len(res.json())}件')

    # ── セキュリティログ ──────────────────
    print_section('セキュリティログ')
    res = requests.get(
        f'{BASE_URL}api/analytics/security-logs/?limit=10',
        headers=auth_headers(super_token),
    )
    for log in res.json():
        print(f"  [{log['action']}] {log['email']} {log['ip_address']}")

    # ── 人気ページ ────────────────────────
    print_section('人気ページランキング')
    res = requests.get(
        f'{BASE_URL}api/analytics/popular-pages/?limit=5',
        headers=auth_headers(super_token),
    )
    for i, page in enumerate(res.json(), 1):
        print(f"  {i}. {page['path']} ({page['count']}件)")

    # ── 日別アクセス数 ────────────────────
    print_section('日別アクセス数（過去7日）')
    res = requests.get(
        f'{BASE_URL}api/analytics/daily/?days=7',
        headers=auth_headers(super_token),
    )
    for day in res.json():
        print(f"  {day['date']}: {day['count']}件")

    # ── サイト別集計 ─────────────────────
    print_section('サイト別集計（過去30日）')
    res = requests.get(
        f'{BASE_URL}api/analytics/sites/',
        headers=auth_headers(super_token),
    )
    for site in res.json():
        print(f"  {site['site']:12} | {site['count']}件"
              f" | 平均:{site['avg_response']:.1f}ms"
              f" | エラー:{site['error_count']}件")

    # ── CSVエクスポート ───────────────────
    print_section('CSVエクスポート（アクセスログ）')
    res = requests.get(
        f'{BASE_URL}api/analytics/export/?type=access',
        headers=auth_headers(super_token),
    )
    filename = 'access_log_export.csv'
    with open(filename, 'wb') as f:
        f.write(res.content)
    print(f'  保存完了: {filename}')

    print_section('CSVエクスポート（セキュリティログ）')
    res = requests.get(
        f'{BASE_URL}api/analytics/export/?type=security',
        headers=auth_headers(super_token),
    )
    filename = 'security_log_export.csv'
    with open(filename, 'wb') as f:
        f.write(res.content)
    print(f'  保存完了: {filename}')

    # ── 一般ユーザーはアクセス不可 ────────
    print_section('一般ユーザーのアクセス（403確認）')
    user_token = fetch_token(USER_EMAIL, USER_PASSWORD)
    res = requests.get(
        f'{BASE_URL}api/analytics/summary/',
        headers=auth_headers(user_token),
    )
    print(f'  ステータス: {res.status_code}')  # 403が返るはず