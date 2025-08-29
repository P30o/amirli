import requests
import telebot
import threading
import logging
from flask import Flask, request
import os
import time

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

TOKEN = "5838783352:AAGBJSOdnVlOdvKhbtS8fVnSaz4nhDOzDqU"
WEBHOOK_URL = "https://amirli.onrender.com/webhook"
bot = telebot.TeleBot(TOKEN, threaded=False)

user_states = {}

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

    time.sleep(2)
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

def instagram_login_thread(chat_id, username, password):
    bot.send_message(chat_id, "⏳ جاري تسجيل الدخول...")
    sessionid = get_instagram_sessionid(username, password)
    if sessionid:
        bot.send_message(chat_id, f"✅ تم تسجيل الدخول بنجاح.\nSessionID:\n`{sessionid}`", parse_mode="Markdown")
    else:
        bot.send_message(chat_id, "❌ فشل تسجيل الدخول. تأكد من البيانات وحاول مرة أخرى.")
    user_states.pop(chat_id, None)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("تسجيل دخول انستقرام", callback_data="login_instagram")
    )
    bot.send_message(chat_id, "👋 أهلاً بك في بوت انستقرام!\nاختر وظيفة:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    if call.data == "login_instagram":
        user_states[chat_id] = {'step': 'ask_username'}
        bot.send_message(chat_id, "📝 أرسل اسم المستخدم الخاص بك في انستقرام:")

@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('step') == 'ask_username')
def receive_username(message):
    chat_id = message.chat.id
    user_states[chat_id]['username'] = message.text.strip()
    user_states[chat_id]['step'] = 'ask_password'
    bot.send_message(chat_id, "🔑 أرسل كلمة المرور الخاصة بك:")

@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('step') == 'ask_password')
def receive_password(message):
    chat_id = message.chat.id
    username = user_states[chat_id]['username']
    password = message.text.strip()
    thread = threading.Thread(target=instagram_login_thread, args=(chat_id, username, password))
    thread.start()
    user_states[chat_id]['step'] = None

@app.route('/webhook', methods=['POST'])
def webhook():
    json_str = request.get_data(as_text=True)
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return '!', 200

if __name__ == "__main__":
    bot.remove_webhook()
    time.sleep(1)
    bot.set_webhook(url=WEBHOOK_URL)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
