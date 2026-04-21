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


# test_techlog.py に追加

def get_posts_filtered(category_id=None, tag_id=None,
                        search=None, ordering=None) -> list:
    """検索・フィルタリング付き記事一覧"""
    _url    = f'{BASE_URL}api/techlog/posts/'
    params  = {}
    if category_id: params['category'] = category_id
    if tag_id:      params['tag']      = tag_id
    if search:      params['search']   = search
    if ordering:    params['ordering'] = ordering

    response = requests.get(_url, params=params)
    logger.debug({'get_posts_filtered status': response.status_code, 'params': params})
    return response.json()


def get_my_posts(_token: str, _status: str = None,
                 _category_id: int = None, _search: str = None,
                 _ordering: str = None) -> list:
    """自分の記事一覧（下書き含む）"""
    _url   = f'{BASE_URL}api/techlog/posts/my/'
    params = {}
    if _status:      params['status']   = _status
    if _category_id: params['category'] = _category_id
    if _search:      params['search']   = _search
    if _ordering:    params['ordering'] = _ordering

    response = requests.get(_url, params=params, headers=auth_headers(_token))
    logger.debug({'get_my_posts status': response.status_code, 'params': params})
    return response.json()


# ── メインに追加 ──────────────────────────

if __name__ == '__main__':
    EMAIL    = 'testuser@example.com'
    PASSWORD = 'testuser'

    print_section('ログイン')
    token = fetch_token(EMAIL, PASSWORD)
    if not token:
        print('ログイン失敗。終了します。')
        sys.exit(1)

    categories  = get_categories()
    tags        = get_tags()
    category_id = categories[0]['id'] if categories else None
    tag_ids     = [t['id'] for t in tags[:2]] if tags else []
    tag_id      = tags[0]['id'] if tags else None

    # テスト用記事を複数作成
    print_section('記事作成（複数）')
    post1 = create_post(
        token,
        'DjangoでJWT認証を実装する',
        '## はじめに\n\nDjangoとSimpleJWTの解説です。',
        category_id, tag_ids, 'published',
    )
    post2 = create_post(
        token,
        'Linuxのネットワーク設定まとめ',
        '## はじめに\n\nLinuxのip コマンドの使い方を解説します。',
        category_id, tag_ids, 'published',
    )
    post3 = create_post(
        token,
        'SLURM設定の基本',
        '## はじめに\n\nHPCクラスタのSLURMジョブスケジューラの設定方法です。',
        category_id, [], 'draft',  # 下書き
    )
    post1_id = post1.get('id')
    post2_id = post2.get('id')

    # ── フィルタリングテスト ───────────────
    print_section('カテゴリで絞り込み')
    results = get_posts_filtered(category_id=category_id)
    print(f'  件数: {len(results)}件')
    for p in results:
        print(f"  {p['title']}")

    print_section('タグで絞り込み')
    results = get_posts_filtered(tag_id=tag_id)
    print(f'  件数: {len(results)}件')
    for p in results:
        print(f"  {p['title']}")

    print_section('キーワード検索（Django）')
    results = get_posts_filtered(search='Django')
    print(f'  件数: {len(results)}件')
    for p in results:
        print(f"  {p['title']}")

    print_section('キーワード検索（Linux）')
    results = get_posts_filtered(search='Linux')
    print(f'  件数: {len(results)}件')
    for p in results:
        print(f"  {p['title']}")

    print_section('閲覧数順ソート')
    results = get_posts_filtered(ordering='views')
    for p in results:
        print(f"  閲覧:{p['views']} {p['title']}")

    print_section('カテゴリ + キーワードの組み合わせ')
    results = get_posts_filtered(category_id=category_id, search='Django')
    print(f'  件数: {len(results)}件')
    for p in results:
        print(f"  {p['title']}")

    # ── 自分の記事一覧 ────────────────────
    print_section('自分の記事一覧（全て）')
    my_posts = get_my_posts(token)
    print(f'  件数: {len(my_posts)}件')
    for p in my_posts:
        print(f"  [{p['status']}] {p['title']}")

    print_section('自分の記事一覧（下書きのみ）')
    drafts = get_my_posts(token, _status='draft')
    print(f'  件数: {len(drafts)}件')
    for p in drafts:
        print(f"  [{p['status']}] {p['title']}")

    print_section('自分の記事一覧（キーワード検索）')
    results = get_my_posts(token, _search='Django')
    print(f'  件数: {len(results)}件')
    for p in results:
        print(f"  [{p['status']}] {p['title']}")

    print_section('自分の記事一覧（閲覧数順）')
    results = get_my_posts(token, _ordering='views')
    for p in results:
        print(f"  閲覧:{p['views']} [{p['status']}] {p['title']}")

    print_section('自分の記事一覧（下書き + キーワード）')
    results = get_my_posts(token, _status='draft', _search='SLURM')
    print(f'  件数: {len(results)}件')
    for p in results:
        print(f"  [{p['status']}] {p['title']}")

    # ── クリーンアップ ────────────────────
    print_section('テスト記事削除')
    print(delete_post(token, post1_id))
    print(delete_post(token, post2_id))
    print(delete_post(token, post3.get('id')))
