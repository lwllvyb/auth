'''用法：python client.py'''
import requests

def signup(username, password):
    '''Sign up a new user.'''
    response = requests.post('http://localhost:8000/signup', timeout=300, json={
        'username': username,
        'password': password,
    })

    if response.status_code == 200:
        print("用户成功创建！")
    else:
        print(f"错误：{response.json()['error']}")

def login(username, password):
    '''Log in an existing user.'''
    response = requests.post('http://localhost:8000/login', timeout=300, json={
        'username': username,
        'password': password,
    })

    if response.status_code == 200:
        print("登录成功！")
        return response.cookies['token']
    else:
        print(f"错误：{response.json()['error']}")

def logout(session_cookie):
    '''Log out an existing user.'''
    response = requests.post('http://localhost:8000/logout', timeout=300, cookies={
        'token': session_cookie,
    })

    if response.status_code == 200:
        print("登出成功！")
    else:
        print(f"错误：{response.json()['error']}")

def validate(session_cookie):
    '''Validate a cookie.'''
    response = requests.get('http://localhost:8000/validate', timeout=300, cookies={
        'token': session_cookie,
    })

    if response.status_code == 200:
        print("Cookie 验证成功！")
    else:
        print(f"错误：{response.json()['error']}")

if __name__ == '__main__':
    USERNAME = 'testuser'
    PASSWORD = 'testpassword'

    signup(USERNAME, PASSWORD)
    SESSION_COOKIE = login(USERNAME, PASSWORD)
    validate(SESSION_COOKIE)
    logout(SESSION_COOKIE)
