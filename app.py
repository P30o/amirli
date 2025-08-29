import requests
import time
from flask import Flask, request
import telebot

TOKEN = "5838783352:AAGBJSOdnVlOdvKhbtS8fVnSaz4nhDOzDqU"
WEBHOOK_URL = "https://amirli.onrender.com/webhook"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

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
        return None

    if login_resp.status_code == 200 and resp_json.get("authenticated"):
        sessionid = session.cookies.get("sessionid")
        return sessionid
    else:
        return None

user_states = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أرسل اسم المستخدم الخاص بإنستغرام:")

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    chat_id = message.chat.id
    if chat_id not in user_states:
        user_states[chat_id] = {'step': 'username'}
        user_states[chat_id]['username'] = message.text
        bot.send_message(chat_id, "أرسل كلمة المرور الخاصة بإنستغرام:")
    elif user_states[chat_id]['step'] == 'username':
        user_states[chat_id]['username'] = message.text
        user_states[chat_id]['step'] = 'password'
        bot.send_message(chat_id, "أرسل كلمة المرور الخاصة بإنستغرام:")
    elif user_states[chat_id]['step'] == 'password':
        username = user_states[chat_id]['username']
        password = message.text
        bot.send_message(chat_id, "جاري تسجيل الدخول...")
        sessionid = get_instagram_sessionid(username, password)
        if sessionid:
            bot.send_message(chat_id, f"Session ID: {sessionid}")
        else:
            bot.send_message(chat_id, "فشل تسجيل الدخول. تأكد من البيانات وحاول مرة أخرى.")
        user_states.pop(chat_id)

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_str = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_str)
        bot.process_new_updates([update])
        return ''
    return 'ok'

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    app.run(host="0.0.0.0", port=5000)
