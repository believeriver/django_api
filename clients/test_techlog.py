# test_techlog.py
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
# カテゴリ・タグ
# ─────────────────────────────────────────

def get_categories() -> list:
    _url = f'{BASE_URL}api/techlog/categories/'
    response = requests.get(_url)
    logger.debug({'get_categories status': response.status_code})
    return response.json()


def get_tags() -> list:
    _url = f'{BASE_URL}api/techlog/tags/'
    response = requests.get(_url)
    logger.debug({'get_tags status': response.status_code})
    return response.json()


# ─────────────────────────────────────────
# 記事操作
# ─────────────────────────────────────────

def get_posts() -> list:
    """公開記事一覧"""
    _url = f'{BASE_URL}api/techlog/posts/'
    response = requests.get(_url)
    logger.debug({'get_posts status': response.status_code})
    return response.json()


def create_post(_token: str, _title: str, _content: str,
                _category_id: int, _tag_ids: list,
                _status: str = 'draft') -> dict:
    """記事作成"""
    _url = f'{BASE_URL}api/techlog/posts/'
    response = requests.post(_url, json={
        'title':       _title,
        'content':     _content,
        'category_id': _category_id,
        'tag_ids':     _tag_ids,
        'status':      _status,
    }, headers=auth_headers(_token))
    logger.debug({'create_post status': response.status_code})
    return response.json()


def get_post(_post_id: str) -> dict:
    """記事詳細"""
    _url = f'{BASE_URL}api/techlog/posts/{_post_id}/'
    response = requests.get(_url)
    logger.debug({'get_post status': response.status_code})
    return response.json()


def update_post(_token: str, _post_id: str, **kwargs) -> dict:
    """記事更新"""
    _url = f'{BASE_URL}api/techlog/posts/{_post_id}/'
    response = requests.patch(_url, json=kwargs, headers=auth_headers(_token))
    logger.debug({'update_post status': response.status_code})
    return response.json()


def delete_post(_token: str, _post_id: str) -> int:
    """記事削除"""
    _url = f'{BASE_URL}api/techlog/posts/{_post_id}/'
    response = requests.delete(_url, headers=auth_headers(_token))
    logger.debug({'delete_post status': response.status_code})
    return response.status_code


# ─────────────────────────────────────────
# いいね
# ─────────────────────────────────────────

def like_post(_token: str, _post_id: str) -> dict:
    """いいね追加"""
    _url = f'{BASE_URL}api/techlog/posts/{_post_id}/like/'
    response = requests.post(_url, headers=auth_headers(_token))
    logger.debug({'like_post status': response.status_code})
    return response.json()


def unlike_post(_token: str, _post_id: str) -> dict:
    """いいね取消"""
    _url = f'{BASE_URL}api/techlog/posts/{_post_id}/like/'
    response = requests.delete(_url, headers=auth_headers(_token))
    logger.debug({'unlike_post status': response.status_code})
    return response.json()


# ─────────────────────────────────────────
# コメント
# ─────────────────────────────────────────

def get_comments(_post_id: str) -> list:
    """コメント一覧"""
    _url = f'{BASE_URL}api/techlog/posts/{_post_id}/comments/'
    response = requests.get(_url)
    logger.debug({'get_comments status': response.status_code})
    return response.json()


def add_comment(_token: str, _post_id: str, _content: str) -> dict:
    """コメント追加"""
    _url = f'{BASE_URL}api/techlog/posts/{_post_id}/comments/'
    response = requests.post(_url, json={
        'content': _content,
    }, headers=auth_headers(_token))
    logger.debug({'add_comment status': response.status_code})
    return response.json()


def update_comment(_token: str, _post_id: str,
                   _comment_id: int, _content: str) -> dict:
    """コメント更新"""
    _url = f'{BASE_URL}api/techlog/posts/{_post_id}/comments/{_comment_id}/'
    response = requests.patch(_url, json={
        'content': _content,
    }, headers=auth_headers(_token))
    logger.debug({'update_comment status': response.status_code})
    return response.json()


def delete_comment(_token: str, _post_id: str, _comment_id: int) -> int:
    """コメント削除"""
    _url = f'{BASE_URL}api/techlog/posts/{_post_id}/comments/{_comment_id}/'
    response = requests.delete(_url, headers=auth_headers(_token))
    logger.debug({'delete_comment status': response.status_code})
    return response.status_code


# ─────────────────────────────────────────
# 表示ヘルパー
# ─────────────────────────────────────────

def print_section(title: str):
    print(f'\n{"=" * 10} {title} {"=" * 10}')


def print_post(post: dict):
    print(f"  ID      : {post.get('id')}")
    print(f"  タイトル: {post.get('title')}")
    print(f"  著者    : {post.get('author', {}).get('username')}")
    print(f"  カテゴリ: {post.get('category', {}).get('name')}")
    tags = [t['name'] for t in post.get('tags', [])]
    print(f"  タグ    : {', '.join(tags) if tags else 'なし'}")
    print(f"  状態    : {post.get('status')}")
    print(f"  閲覧数  : {post.get('views')}")
    print(f"  いいね  : {post.get('like_count')}")
    print(f"  コメント: {post.get('comment_count')}件")


# ─────────────────────────────────────────
# メイン
# ─────────────────────────────────────────

if __name__ == '__main__':
    EMAIL    = 'nono@example.com'
    PASSWORD = 'pass1234'

    # ── ログイン ──────────────────────────
    print_section('ログイン')
    token = fetch_token(EMAIL, PASSWORD)
    if not token:
        print('ログイン失敗。終了します。')
        sys.exit(1)
    print('トークン取得成功')

    # ── カテゴリ・タグ確認 ────────────────
    print_section('カテゴリ一覧')
    categories = get_categories()
    print(categories)

    print_section('タグ一覧')
    tags = get_tags()
    print(tags)

    # カテゴリ・タグが空の場合はadminで事前に登録が必要
    if not categories:
        print('\n⚠ カテゴリが登録されていません。admin画面から登録してください。')
        print('  http://localhost:8000/admin/')
        sys.exit(1)

    category_id = categories[0]['id']
    tag_ids     = [t['id'] for t in tags[:2]] if tags else []

    # ── 記事作成（下書き）────────────────
    print_section('記事作成（下書き）')
    post = create_post(
        token,
        'DjangoでJWT認証を実装する',
        '## はじめに\n\nDjango REST FrameworkとSimpleJWTを使った認証APIの実装方法を解説します。\n\n## インストール\n\n```bash\npip install djangorestframework-simplejwt\n```\n',
        category_id,
        tag_ids,
        'draft',
    )
    print_post(post)
    post_id = post.get('id')

    # ── 記事一覧（下書きは表示されないはず）──
    print_section('記事一覧（公開済みのみ）')
    posts = get_posts()
    print(f'  公開記事数: {len(posts)}件')

    # ── 記事を公開 ───────────────────────
    print_section('記事を公開に変更')
    updated = update_post(token, post_id, status='published')
    print_post(updated)

    # ── 記事一覧（公開後）─────────────────
    print_section('記事一覧（公開後）')
    posts = get_posts()
    print(f'  公開記事数: {len(posts)}件')
    for p in posts:
        print(f"  [{p['status']}] {p['title']} | 閲覧:{p['views']} いいね:{p['like_count']}")

    # ── 記事詳細（閲覧数カウントアップ確認）─
    print_section('記事詳細（閲覧数カウントアップ）')
    detail = get_post(post_id)
    print_post(detail)
    detail = get_post(post_id)  # 2回目
    print(f'  閲覧数（2回アクセス後）: {detail.get("views")}')

    # ── いいね ───────────────────────────
    print_section('いいね追加')
    print(like_post(token, post_id))

    print_section('いいね重複（エラー確認）')
    print(like_post(token, post_id))  # 400が返るはず

    print_section('いいね取消')
    print(unlike_post(token, post_id))

    # ── コメント ─────────────────────────
    print_section('コメント追加')
    comment = add_comment(token, post_id, 'とても参考になりました！')
    print(comment)
    comment_id = comment.get('id')

    print_section('コメント一覧')
    comments = get_comments(post_id)
    for c in comments:
        print(f"  [{c['id']}] {c['author']['username']}: {c['content']}")

    print_section('コメント更新')
    print(update_comment(token, post_id, comment_id, '大変参考になりました！ありがとうございます。'))

    print_section('コメント削除')
    print(f'削除ステータス: {delete_comment(token, post_id, comment_id)}')

    # ── 記事削除 ─────────────────────────
    print_section('記事削除')
    print(f'削除ステータス: {delete_post(token, post_id)}')

    # ── 削除後の一覧確認 ──────────────────
    print_section('削除後の記事一覧')
    posts = get_posts()
    print(f'  公開記事数: {len(posts)}件')
