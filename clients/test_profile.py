# test_profile.py
import requests
import logging
import sys

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger(__name__)

BASE_URL = 'http://127.0.0.1:8000/'


def print_section(title):
    print(f'\n{"=" * 10} {title} {"=" * 10}')


if __name__ == '__main__':

    # ── プロフィール取得（認証不要）────────
    print_section('プロフィール取得')
    res = requests.get(f'{BASE_URL}api/profile/')
    logger.debug({'status': res.status_code})

    if res.status_code == 404:
        print('プロフィールが未登録です。admin画面から登録してください。')
        print('http://localhost:8000/admin/')
        sys.exit(1)

    data = res.json()
    print(f"  名前      : {data['name']}")
    print(f"  ニック    : {data['nickname']}")
    print(f"  場所      : {data['location']}")
    print(f"  自己紹介  : {data['bio'][:50]}...")

    print(f"\n  --- スキル ({len(data['skills'])}件) ---")
    for s in data['skills']:
        level = f" Lv.{s['level']}" if s['level'] else ''
        print(f"  [{s['category_label']}] {s['name']}{level}")

    print(f"\n  --- 業務経験 ({len(data['careers'])}件) ---")
    for c in data['careers']:
        end = '現在' if c['is_current'] else c['end_date']
        print(f"  {c['title']} | {c['start_date']} 〜 {end}")

    print(f"\n  --- リンク ({len(data['links'])}件) ---")
    for l in data['links']:
        print(f"  [{l['platform']}] {l['url']}")

