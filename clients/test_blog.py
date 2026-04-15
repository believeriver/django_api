# test_blog.py
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
    _url = f'{BASE_URL}api/blog/categories/'
    response = requests.get(_url)
    logger.debug({'get_categories status': response.status_code})
    return response.json()


def get_tags() -> list:
    _url = f'{BASE_URL}api/blog/tags/'
    response = requests.get(_url)
    logger.debug({'get_tags status': response.status_code})
    return response.json()


# ─────────────────────────────────────────
# 記事操作
# ─────────────────────────────────────────

def get_posts(**kwargs) -> list:
    """
    公開記事一覧
    kwargs: category, tag, search, ordering
    """
    _url     = f'{BASE_URL}api/blog/posts/'
    response = requests.get(_url, params=kwargs)
    logger.debug({'get_posts status': response.status_code, 'params': kwargs})
    return response.json()


def create_post(_token: str, _title: str, _content: str,
                _category_id: int, _tag_ids: list,
                _summary: str = '', _location: str = '',
                _status: str = 'draft') -> dict:
    """記事作成（superuserのみ・multipart形式）"""
    _url = f'{BASE_URL}api/blog/posts/'
    response = requests.post(_url, data={
        'title':       _title,
        'content':     _content,
        'summary':     _summary,
        'category_id': _category_id,
        'tag_ids':     _tag_ids,
        'location':    _location,
        'status':      _status,
    }, headers=auth_headers(_token))
    logger.debug({'create_post status': response.status_code})
    return response.json()


def get_post(_post_id: str) -> dict:
    """記事詳細"""
    _url = f'{BASE_URL}api/blog/posts/{_post_id}/'
    response = requests.get(_url)
    logger.debug({'get_post status': response.status_code})
    return response.json()


def update_post(_token: str, _post_id: str, **kwargs) -> dict:
    """記事更新（superuserのみ）"""
    _url = f'{BASE_URL}api/blog/posts/{_post_id}/'
    response = requests.patch(
        _url,
        data=kwargs,
        headers=auth_headers(_token),
    )
    logger.debug({'update_post status': response.status_code})
    return response.json()


def delete_post(_token: str, _post_id: str) -> int:
    """記事削除（superuserのみ）"""
    _url = f'{BASE_URL}api/blog/posts/{_post_id}/'
    response = requests.delete(_url, headers=auth_headers(_token))
    logger.debug({'delete_post status': response.status_code})
    return response.status_code


# ─────────────────────────────────────────
# 画像アップロード
# ─────────────────────────────────────────

def upload_image(_token: str, _post_id: str,
                 _image_path: str, _caption: str = '') -> dict:
    """本文中画像アップロード（superuserのみ）"""
    _url = f'{BASE_URL}api/blog/posts/{_post_id}/images/'
    with open(_image_path, 'rb') as f:
        response = requests.post(
            _url,
            files={'image': f},
            data={'caption': _caption},
            headers=auth_headers(_token),
        )
    logger.debug({'upload_image status': response.status_code})
    return response.json()


# ─────────────────────────────────────────
# いいね
# ─────────────────────────────────────────

def like_post(_token: str, _post_id: str) -> dict:
    _url = f'{BASE_URL}api/blog/posts/{_post_id}/like/'
    response = requests.post(_url, headers=auth_headers(_token))
    logger.debug({'like_post status': response.status_code})
    return response.json()


def unlike_post(_token: str, _post_id: str) -> dict:
    _url = f'{BASE_URL}api/blog/posts/{_post_id}/like/'
    response = requests.delete(_url, headers=auth_headers(_token))
    logger.debug({'unlike_post status': response.status_code})
    return response.json()


# ─────────────────────────────────────────
# コメント
# ─────────────────────────────────────────

def get_comments(_post_id: str) -> list:
    _url = f'{BASE_URL}api/blog/posts/{_post_id}/comments/'
    response = requests.get(_url)
    logger.debug({'get_comments status': response.status_code})
    return response.json()


def add_comment(_token: str, _post_id: str, _content: str) -> dict:
    _url = f'{BASE_URL}api/blog/posts/{_post_id}/comments/'
    response = requests.post(
        _url,
        json={'content': _content},
        headers=auth_headers(_token),
    )
    logger.debug({'add_comment status': response.status_code})
    return response.json()


def update_comment(_token: str, _post_id: str,
                   _comment_id: int, _content: str) -> dict:
    _url = f'{BASE_URL}api/blog/posts/{_post_id}/comments/{_comment_id}/'
    response = requests.patch(
        _url,
        json={'content': _content},
        headers=auth_headers(_token),
    )
    logger.debug({'update_comment status': response.status_code})
    return response.json()


def delete_comment(_token: str, _post_id: str, _comment_id: int) -> int:
    _url = f'{BASE_URL}api/blog/posts/{_post_id}/comments/{_comment_id}/'
    response = requests.delete(_url, headers=auth_headers(_token))
    logger.debug({'delete_comment status': response.status_code})
    return response.status_code


# ─────────────────────────────────────────
# 表示ヘルパー
# ─────────────────────────────────────────

def print_section(title: str):
    print(f'\n{"=" * 10} {title} {"=" * 10}')


def print_post(post: dict):
    print(f"  ID        : {post.get('id')}")
    print(f"  タイトル  : {post.get('title')}")
    print(f"  著者      : {post.get('author', {}).get('username')}")
    print(f"  カテゴリ  : {post.get('category', {}).get('name')}")
    tags = [t['name'] for t in post.get('tags', [])]
    print(f"  タグ      : {', '.join(tags) if tags else 'なし'}")
    print(f"  場所      : {post.get('location') or 'なし'}")
    print(f"  状態      : {post.get('status')}")
    print(f"  閲覧数    : {post.get('views')}")
    print(f"  いいね    : {post.get('like_count')}")
    print(f"  コメント  : {post.get('comment_count')}件")
    print(f"  読了時間  : {post.get('reading_time')}分")
    print(f"  サムネイル: {post.get('thumbnail_url') or 'なし'}")


# ─────────────────────────────────────────
# メイン
# ─────────────────────────────────────────

if __name__ == '__main__':
    # superuserのメール・パスワードを設定
    SUPER_EMAIL    = 'admin@example.com'
    SUPER_PASSWORD = 'adminpass'



    # 一般ユーザー（コメント・いいねテスト用）
    USER_EMAIL    = 'nono@example.com'
    USER_PASSWORD = 'pass1234'

    # ── ログイン ──────────────────────────
    print_section('superuserログイン')
    super_token = fetch_token(SUPER_EMAIL, SUPER_PASSWORD)
    if not super_token:
        print('superuserログイン失敗。終了します。')
        sys.exit(1)
    print('superuserトークン取得成功')

    print_section('一般ユーザーログイン')
    user_token = fetch_token(USER_EMAIL, USER_PASSWORD)
    if not user_token:
        print('一般ユーザーログイン失敗。終了します。')
        sys.exit(1)
    print('一般ユーザートークン取得成功')

    # ── カテゴリ・タグ確認 ────────────────
    print_section('カテゴリ一覧')
    categories = get_categories()
    print(categories)

    print_section('タグ一覧')
    tags = get_tags()
    print(tags)

    if not categories:
        print('\n⚠ カテゴリが未登録です。admin画面から登録してください。')
        print('  http://localhost:8000/admin/')
        sys.exit(1)

    category_id = categories[0]['id']
    tag_ids     = [t['id'] for t in tags[:2]] if tags else []

    # ── 記事作成（下書き）────────────────
    print_section('記事作成（下書き）')
    post = create_post(
        super_token,
        '早朝5時の習慣が、一日をどう変えるか',
        '## はじめに\n\n起床直後の静けさの中でコードを書く。\n\n## 朝のルーティン\n\n5時に起きて、まずコーヒーを淹れる。',
        category_id,
        tag_ids,
        '起床直後の静けさの中で読書とコードを書く。それだけで、夜には何かが違う気がする。',  # summary
        'Nagasaki',  # location
        'draft',  # _status
    )
    print_post(post)
    post_id = post.get('id')

    # ── 一般ユーザーは記事作成不可 ────────
    print_section('一般ユーザーによる記事作成（403確認）')
    res = create_post(
        user_token,
        'テスト記事',
        '本文',
        category_id,
        [],
    )
    print(f'  ステータス確認: {res}')  # 403が返るはず

    # ── 記事一覧（下書きは表示されない）───
    print_section('記事一覧（公開前）')
    posts = get_posts()
    print(f'  公開記事数: {len(posts)}件')

    # ── 記事を公開 ───────────────────────
    print_section('記事を公開に変更')
    updated = update_post(super_token, post_id, status='published')
    print_post(updated)

    # ── 記事一覧（公開後）─────────────────
    print_section('記事一覧（公開後）')
    posts = get_posts()
    print(f'  公開記事数: {len(posts)}件')
    for p in posts:
        print(f"  [{p['status']}] {p['title']}"
              f" | 閲覧:{p['views']}"
              f" | いいね:{p['like_count']}"
              f" | 読了:{p['reading_time']}分")

    # ── 記事詳細（閲覧数カウントアップ）───
    print_section('記事詳細（閲覧数カウントアップ）')
    get_post(post_id)
    detail = get_post(post_id)
    print(f'  閲覧数（2回アクセス後）: {detail.get("views")}')

    # ── 検索・フィルタリング ──────────────
    print_section('キーワード検索（朝活）')
    results = get_posts(search='朝')
    print(f'  件数: {len(results)}件')

    print_section('カテゴリで絞り込み')
    results = get_posts(category=category_id)
    print(f'  件数: {len(results)}件')

    print_section('閲覧数順ソート')
    results = get_posts(ordering='views')
    for p in results:
        print(f"  閲覧:{p['views']} {p['title']}")

    # ── いいね ───────────────────────────
    print_section('いいね追加（一般ユーザー）')
    print(like_post(user_token, post_id))

    print_section('いいね重複（エラー確認）')
    print(like_post(user_token, post_id))  # 400

    print_section('いいね取消')
    print(unlike_post(user_token, post_id))

    # ── コメント ─────────────────────────
    print_section('コメント追加')
    comment = add_comment(user_token, post_id, 'とても参考になりました！')
    print(comment)
    comment_id = comment.get('id')

    print_section('コメント一覧')
    comments = get_comments(post_id)
    for c in comments:
        print(f"  [{c['id']}] {c['author']['username']}: {c['content']}")

    print_section('コメント更新')
    print(update_comment(user_token, post_id, comment_id,
                         '大変参考になりました！ありがとうございます。'))

    print_section('コメント削除')
    print(f'削除ステータス: {delete_comment(user_token, post_id, comment_id)}')

    # ── archivedステータス確認 ────────────
    print_section('記事をarchivedに変更')
    update_post(super_token, post_id, status='archived')
    posts = get_posts()
    print(f'  archived後の公開記事数: {len(posts)}件')  # 0件になるはず

    # ── 記事削除 ─────────────────────────
    print_section('記事削除')
    print(f'削除ステータス: {delete_post(super_token, post_id)}')

    print_section('削除後の記事一覧')
    posts = get_posts()
    print(f'  公開記事数: {len(posts)}件')