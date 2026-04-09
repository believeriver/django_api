import requests
import logging
import sys

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger(__name__)

BASE_URL = 'http://127.0.0.1:8000/'


def delete_account(_access_token: str, _password: str):
    _url = f'{BASE_URL}api/auth/profile/'
    response = requests.delete(
        _url,
        json={'password': _password},
        headers={'Authorization': f'Bearer {_access_token}'},
    )
    logger.debug({'delete_account status': response.status_code})
    # 204はボディなしなので status_code のみ返す
    return response.status_code


if __name__ == '__main__':
    email    = 'nono_new@example.com'
    password = 'pass1234'

    # ログイン
    login_res = requests.post(
        f'{BASE_URL}api/auth/login/',
        json={'email': email, 'password': password},
    )
    access_token = login_res.json().get('access')

    # パスワード誤りで削除試行
    print('--- パスワード誤り ---')
    print(delete_account(access_token, 'wrongpassword'))  # 400

    # 正しいパスワードで削除
    print('--- アカウント削除 ---')
    print(delete_account(access_token, password))  # 204

    # 削除後にログイン試行
    print('--- 削除後ログイン試行 ---')
    res = requests.post(
        f'{BASE_URL}api/auth/login/',
        json={'email': email, 'password': password},
    )
    print({'status': res.status_code, 'detail': res.json()})
