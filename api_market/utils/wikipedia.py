import requests
import logging

logger = logging.getLogger(__name__)


def fetch_wikipedia_info(company_name: str) -> dict:
    """
    Wikipedia API から企業情報を取得

    Returns:
        {
            'extract': str,  # 企業概要テキスト
            'url': str,      # WikipediaページURL
            'website': str,  # 企業公式サイトURL
        }
    """
    query = company_name \
        .replace('(株)', '') \
        .replace('株式会社', '') \
        .replace('（株）', '') \
        .strip()

    headers = {
        'User-Agent': 'believeriver-portfolio/1.0 (contact: nobuyuki.galois@gmail.com)'
    }

    # ① まず直接ページタイトルとして取得を試みる
    result = _fetch_by_title(query, headers)
    if result:
        return result

    # ② 見つからない場合は検索クエリで試みる
    search_queries = [
        f'{query} 株式会社',
        f'{query} 企業',
        query,
    ]

    for search_query in search_queries:
        result = _search_and_fetch(search_query, query, headers)
        if result:
            return result

    logger.warning(f'Wikipedia: 有効な情報なし → {query}')
    return {}


def _fetch_by_title(title: str, headers: dict) -> dict:
    """ページタイトルを直接指定して取得"""
    try:
        api_url = 'https://ja.wikipedia.org/w/api.php'

        detail_params = {
            'action':      'query',
            'prop':        'extracts|info',
            'titles':      title,
            'exintro':     True,
            'explaintext': True,
            'inprop':      'url',
            'format':      'json',
        }
        detail_res  = requests.get(api_url, params=detail_params, headers=headers)
        detail_data = detail_res.json()
        pages       = detail_data.get('query', {}).get('pages', {})
        page        = next(iter(pages.values()))

        # ページが存在しない場合（page id が -1）
        if page.get('pageid', -1) == -1:
            logger.info(f'Wikipedia: ページなし（直接取得）→ {title}')
            return {}

        extract  = page.get('extract', '')
        wiki_url = page.get('fullurl', '')

        if not extract:
            return {}

        # 企業情報らしいかチェック
        company_keywords = ['会社', '企業', '事業', '製品', '販売', '製造', '設立', '本社']
        if not any(keyword in extract for keyword in company_keywords):
            logger.warning(f'Wikipedia: 企業情報でない可能性（直接取得）→ {title}')
            return {}

        logger.info(f'Wikipedia: 直接取得成功 → {title}')
        website = _find_official_website(api_url, title, headers)

        return {
            'extract': extract[:2000],
            'url':     wiki_url,
            'website': website,
        }

    except Exception as e:
        logger.error(f'Wikipedia 直接取得エラー: {e}')
        return {}


def _search_and_fetch(search_query: str, original_query: str, headers: dict) -> dict:
    """検索して企業関連ページを取得"""
    try:
        api_url = 'https://ja.wikipedia.org/w/api.php'

        # ── 検索 ──────────────────────────────
        search_params = {
            'action':   'query',
            'list':     'search',
            'srsearch': search_query,
            'srlimit':  3,
            'format':   'json',
        }
        search_res  = requests.get(api_url, params=search_params, headers=headers)
        search_data = search_res.json()
        results     = search_data.get('query', {}).get('search', [])

        if not results:
            return {}

        # ── 企業らしいタイトルを優先 ──────────
        exclude_words = [
            '山', '川', '峰', '岳', '湖', '島',
            '市', '町', '村', '県', '区', '連峰', '高原',
        ]
        page_title = None
        for result in results:
            title = result['title']
            if not any(word in title for word in exclude_words):
                page_title = title
                break

        if not page_title:
            page_title = results[0]['title']

        logger.info(f'Wikipedia: ページタイトル → {page_title}')

        # ── ページ詳細を取得 ──────────────────
        detail_params = {
            'action':      'query',
            'prop':        'extracts|info',
            'titles':      page_title,
            'exintro':     True,
            'explaintext': True,
            'inprop':      'url',
            'format':      'json',
        }
        detail_res  = requests.get(api_url, params=detail_params, headers=headers)
        detail_data = detail_res.json()
        pages       = detail_data.get('query', {}).get('pages', {})
        page        = next(iter(pages.values()))
        extract     = page.get('extract', '')
        wiki_url    = page.get('fullurl', '')

        if not extract:
            return {}

        # ── 企業情報らしいかチェック ──────────
        company_keywords = ['会社', '企業', '事業', '製品', '販売', '製造', '設立', '本社']
        if not any(keyword in extract for keyword in company_keywords):
            logger.warning(f'Wikipedia: 企業情報でない可能性 → {page_title}')
            return {}

        # ── 公式サイトを取得 ──────────────────
        website = _find_official_website(api_url, page_title, headers)

        return {
            'extract': extract[:2000],
            'url':     wiki_url,
            'website': website,
        }

    except Exception as e:
        logger.error(f'Wikipedia 検索エラー: {e}')
        return {}


def _find_official_website(api_url: str, page_title: str, headers: dict) -> str:
    """Wikipedia の外部リンクから公式サイトを探す"""
    try:
        params = {
            'action':  'query',
            'prop':    'extlinks',
            'titles':  page_title,
            'ellimit': 20,
            'format':  'json',
        }
        res   = requests.get(api_url, params=params, headers=headers)
        data  = res.json()
        pages = data.get('query', {}).get('pages', {})
        page  = next(iter(pages.values()))
        links = page.get('extlinks', [])

        # SNS・Wikipedia・ニュースサイト等を除外
        exclude_domains = [
            'wikipedia', 'twitter', 'facebook', 'instagram',
            'linkedin', 'youtube', 'amazon', 'rakuten',
            'nikkei', 'bloomberg', 'reuters', 'yahoo',
            'google', 'bing', 'wikidata',
        ]

        for link in links:
            url = link.get('*', '')
            if not url.startswith('http'):
                continue
            if any(domain in url for domain in exclude_domains):
                continue
            if url.endswith('.pdf'):  # ← PDFを除外
                continue
            if '.co.jp' in url or '.com' in url or '.jp' in url:
                return url

        return ''

    except Exception:
        return ''