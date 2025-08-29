import requests
import telebot
import threading
import logging
from flask import Flask, request, jsonify
import os
import time
import json
import re

# إعدادات التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# تهيئة Flask و Telebot
app = Flask(__name__)

# التوكن الخاص بالبوت - تأكد من صحته
TOKEN = "5838783352:AAGBJSOdnVlOdvKhbtS8fVnSaz4nhDOzDqU"
WEBHOOK_URL = "https://amirli.onrender.com/webhook"
bot = telebot.TeleBot(TOKEN, threaded=False)

# تخزين حالة المستخدمين
user_states = {}

def get_instagram_sessionid(username, password):
    """
    الحصول على sessionid من انستقرام - الإصدار المحدث
    """
    login_url = "https://www.instagram.com/accounts/login/ajax/"
    session = requests.Session()
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://www.instagram.com/accounts/login/",
        "Accept": "*/*",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Language": "en-US,en;q=0.9",
        "Origin": "https://www.instagram.com",
        "Host": "www.instagram.com",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive"
    }
    
    try:
        # الحصول على الصفحة الرئيسية واستخراج CSRF token
        home_page = session.get("https://www.instagram.com/accounts/login/", headers=headers, timeout=30)
        csrf_token = re.search(r'"csrf_token":"([^"]+)"', home_page.text).group(1)
        
        if not csrf_token:
            logger.error("Failed to get CSRF token")
            return None
            
        headers["X-CSRFToken"] = csrf_token
        headers["Cookie"] = f"csrftoken={csrf_token}; ig_did=0;"

        time.sleep(2)
        
        # تحضير البيانات للدخول - الطريقة المحدثة
        timestamp = int(time.time())
        enc_password = f"#PWD_INSTAGRAM_BROWSER:0:{timestamp}:{password}"
        
        payload = {
            "username": username,
            "enc_password": enc_password,
            "queryParams": "{}",
            "optIntoOneTap": "false",
            "trustedDeviceRecords": "{}"
        }
        
        # محاولة الدخول
        login_resp = session.post(login_url, data=payload, headers=headers, allow_redirects=True, timeout=30)
        
        if login_resp.status_code != 200:
            logger.error(f"Login failed with status code: {login_resp.status_code}")
            return None
            
        try:
            resp_json = login_resp.json()
        except json.JSONDecodeError:
            logger.error("Failed to parse JSON response")
            return None

        if resp_json.get("authenticated") and resp_json.get("status") == "ok":
            sessionid = session.cookies.get("sessionid")
            if sessionid:
                logger.info("Login successful")
                return sessionid
            else:
                logger.error("Session ID not found in cookies")
                return None
        else:
            error_message = resp_json.get("message", "Unknown error")
            logger.error(f"Authentication failed: {error_message}")
            return None
            
    except requests.exceptions.Timeout:
        logger.error("Request timeout")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return None

def instagram_login_thread(chat_id, username, password):
    """
    عملية تسجيل الدخول في خيط منفصل
    """
    try:
        bot.send_message(chat_id, "⏳ جاري تسجيل الدخول...")
        sessionid = get_instagram_sessionid(username, password)
        
        if sessionid:
            bot.send_message(
                chat_id, 
                f"✅ تم تسجيل الدخول بنجاح.\n\nSessionID:\n`{sessionid}`", 
                parse_mode="Markdown"
            )
        else:
            bot.send_message(
                chat_id, 
                "❌ فشل تسجيل الدخول. تأكد من صحة البيانات وحاول مرة أخرى.\n\nملاحظة: قد تحتاج إلى تفعيل التحقق بخطوتين أو قد يكون الحساب محميًا بإعدادات أمان إضافية."
            )
            
    except Exception as e:
        logger.error(f"Error in login thread: {e}")
        bot.send_message(chat_id, "❌ حدث خطأ أثناء المعالجة. حاول مرة أخرى.")
    
    finally:
        # تنظيف حالة المستخدم
        if chat_id in user_states:
            user_states.pop(chat_id)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """
    معالج أمر /start
    """
    try:
        chat_id = message.chat.id
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(
            telebot.types.InlineKeyboardButton(
                "تسجيل دخول انستقرام", 
                callback_data="login_instagram"
            )
        )
        
        welcome_text = """
        👋 أهلاً بك في بوت انستقرام!

        📱 يمكنك الحصول على SessionID لحسابك في انستقرام

        🔒 بياناتك محمية ولا يتم تخزينها
        
        ⚠️ ملاحظة: إذا كان لديك تحقق بخطوتين مفعل، قد تحتاج إلى تعطيله مؤقتاً
        """
        
        bot.send_message(
            chat_id, 
            welcome_text, 
            reply_markup=markup
        )
        
    except Exception as e:
        logger.error(f"Error in start handler: {e}")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    """
    معالج الأزرارInline
    """
    try:
        chat_id = call.message.chat.id
        
        if call.data == "login_instagram":
            user_states[chat_id] = {'step': 'ask_username'}
            bot.send_message(chat_id, "📝 أرسل اسم المستخدم الخاص بك في انستقرام:")
            
    except Exception as e:
        logger.error(f"Error in callback handler: {e}")

@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('step') == 'ask_username')
def receive_username(message):
    """
    استقبال اسم المستخدم
    """
    try:
        chat_id = message.chat.id
        username = message.text.strip()
        
        if not username:
            bot.send_message(chat_id, "⚠️ يرجى إرسال اسم مستخدم صحيح")
            return
            
        user_states[chat_id]['username'] = username
        user_states[chat_id]['step'] = 'ask_password'
        bot.send_message(chat_id, "🔑 أرسل كلمة المرور الخاصة بك:")
        
    except Exception as e:
        logger.error(f"Error in username handler: {e}")

@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('step') == 'ask_password')
def receive_password(message):
    """
    استقبال كلمة المرور
    """
    try:
        chat_id = message.chat.id
        password = message.text.strip()
        
        if not password:
            bot.send_message(chat_id, "⚠️ يرجى إرسال كلمة مرور صحيحة")
            return
            
        username = user_states[chat_id]['username']
        
        # بدء عملية الدخول في خيط منفصل
        thread = threading.Thread(
            target=instagram_login_thread, 
            args=(chat_id, username, password)
        )
        thread.daemon = True
        thread.start()
        
        # مسح البيانات الحساسة من الذاكرة
        user_states[chat_id]['step'] = 'processing'
        
    except Exception as e:
        logger.error(f"Error in password handler: {e}")
        bot.send_message(chat_id, "❌ حدث خطأ أثناء المعالجة")

@app.route('/')
def home():
    """
    الصفحة الرئيسية للتحقق من عمل السيرفر
    """
    return jsonify({
        "status": "success",
        "message": "Bot is running!",
        "timestamp": time.time()
    }), 200

@app.route('/webhook', methods=['POST'])
def webhook():
    """
    معالج Webhook للبوت
    """
    try:
        if request.headers.get('content-type') == 'application/json':
            json_str = request.get_data().decode('UTF-8')
            update = telebot.types.Update.de_json(json_str)
            bot.process_new_updates([update])
            return 'OK', 200
        else:
            return 'Invalid content type', 400
            
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return 'Error', 500

@app.route('/setwebhook', methods=['GET'])
def set_webhook():
    """
    إعداد Webhook يدوياً
    """
    try:
        bot.remove_webhook()
        time.sleep(1)
        success = bot.set_webhook(url=WEBHOOK_URL)
        
        if success:
            return jsonify({
                "status": "success",
                "message": "Webhook set successfully"
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "Failed to set webhook"
            }), 500
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/health')
def health_check():
    """
    نقطة فحص صحة السيرفر
    """
    return jsonify({"status": "healthy"}), 200

if __name__ == "__main__":
    """
    التشغيل الرئيسي
    """
    try:
        logger.info("Starting bot server...")
        
        # إعداد Webhook تلقائياً
        bot.remove_webhook()
        time.sleep(2)
        bot.set_webhook(url=WEBHOOK_URL)
        
        # تشغيل السيرفر
        port = int(os.environ.get("PORT", 10000))
        app.run(
            host="0.0.0.0",
            port=port,
            debug=False
        )
        
    except Exception as e:
        logger.error(f"Failed to start server: {e}")