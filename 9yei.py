import requests
import time

def get_instagram_sessionid(username, password):
    login_url = "https://www.instagram.com/accounts/login/ajax/"
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://www.instagram.com/accounts/login/",
        "Accept": "*/*",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Language": "en-US,en;q=0.9",
        "Origin": "https://www.instagram.com",
        "Host": "www.instagram.com",
        "Accept-Encoding": "gzip, deflate, br",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty"
    }
    resp = session.get("https://www.instagram.com/accounts/login/", headers=headers)
    csrf_token = resp.cookies.get("csrftoken")
    headers["X-CSRFToken"] = csrf_token
    headers["Cookie"] = f"csrftoken={csrf_token};"

    time.sleep(2)  # Instagram may block fast requests

    payload = {
        "username": username,
        "enc_password": f"#PWD_INSTAGRAM_BROWSER:0:{int(time.time()*1000)}:{password}",
        "queryParams": {},
        "optIntoOneTap": "false"
    }
    login_resp = session.post(login_url, data=payload, headers=headers, allow_redirects=True)
    try:
        resp_json = login_resp.json()
    except Exception:
        print("Response not JSON:", login_resp.text)
        return None

    if login_resp.status_code == 200 and resp_json.get("authenticated"):
        sessionid = session.cookies.get("sessionid")
        print(f"Session ID: {sessionid}")
        return sessionid
    else:
        print("Login failed:", resp_json)
        print("Cookies:", session.cookies.get_dict())
        print("Details:", login_resp.text)
        return None

if __name__ == "__main__":
    username = input("Enter Instagram username: ")
    password = input("Enter Instagram password: ")
    get_instagram_sessionid(username, password)
import requests
import time

def get_instagram_sessionid(username, password):
    login_url = "https://www.instagram.com/accounts/login/ajax/"
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://www.instagram.com/accounts/login/",
        "Accept": "*/*",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Language": "en-US,en;q=0.9",
        "Origin": "https://www.instagram.com",
        "Host": "www.instagram.com",
        "Accept-Encoding": "gzip, deflate, br",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty"
    }
    resp = session.get("https://www.instagram.com/accounts/login/", headers=headers)
    csrf_token = resp.cookies.get("csrftoken")
    headers["X-CSRFToken"] = csrf_token
    headers["Cookie"] = f"csrftoken={csrf_token};"

    time.sleep(2)  # Instagram may block fast requests

    payload = {
        "username": username,
        "enc_password": f"#PWD_INSTAGRAM_BROWSER:0:{int(time.time()*1000)}:{password}",
        "queryParams": {},
        "optIntoOneTap": "false"
    }
    login_resp = session.post(login_url, data=payload, headers=headers, allow_redirects=True)
    try:
        resp_json = login_resp.json()
    except Exception:
        print("Response not JSON:", login_resp.text)
        return None

    if login_resp.status_code == 200 and resp_json.get("authenticated"):
        sessionid = session.cookies.get("sessionid")
        print(f"Session ID: {sessionid}")
        return sessionid
    else:
        print("Login failed:", resp_json)
        print("Cookies:", session.cookies.get_dict())
        print("Details:", login_resp.text)
        return None

if __name__ == "__main__":
    username = input("Enter Instagram username: ")
    password = input("Enter Instagram password: ")
    get_instagram_sessionid(username, password)
