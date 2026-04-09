import requests
import logging
import sys

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger(__name__)

BASE_URL = 'http://127.0.0.1:8000/'

"""
フロントエンド・クライアント側の対応として以下のフローが必要になります。
① AccessToken で API アクセス
        ↓
② 401 が返る（期限切れ）
        ↓
③ RefreshToken で AccessToken を再取得
   POST /api/auth/refresh/
        ↓
④ 新しい AccessToken で再リクエスト
        ↓
⑤ RefreshToken も期限切れ → ログイン画面へ
"""

def request_with_refresh(url: str, access_token: str, refresh_token: str):
    """AccessToken期限切れ時にRefreshTokenで自動再取得"""

    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url, headers=headers)

    # AccessToken期限切れ
    if response.status_code == 401:
        logger.debug('AccessToken expired. Trying refresh...')

        # RefreshTokenで再取得
        refresh_res = requests.post(
            f'{BASE_URL}api/auth/refresh/',
            json={'refresh': refresh_token},
        )

        # RefreshTokenも期限切れ → 再ログインが必要
        if refresh_res.status_code != 200:
            logger.error('RefreshToken expired. Please login again.')
            return None, None, None

        new_access  = refresh_res.json().get('access')
        new_refresh = refresh_res.json().get('refresh')  # ROTATE_REFRESH_TOKENS=Trueの場合
        logger.debug('Token refreshed successfully.')

        # 新しいAccessTokenで再リクエスト
        headers = {'Authorization': f'Bearer {new_access}'}
        response = requests.get(url, headers=headers)

        return response, new_access, new_refresh

    return response, access_token, refresh_token


if __name__ == '__main__':
    email    = 'nono@example.com'
    password = 'pass1234'

    # ログイン
    login_res = requests.post(
        f'{BASE_URL}api/auth/login/',
        json={'email': email, 'password': password},
    )
    access_token = login_res.json().get('access')

    # 現在のプロフィール取得
    print('--- 現在のプロフィール ---')
    profile_url = f'{BASE_URL}api/auth/profile/'
    response, access_token, refresh_token = request_with_refresh(profile_url, access_token, None)
    print({'status': response.status_code, 'data': response.json()})

