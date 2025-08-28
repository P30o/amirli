import os
import telebot
from flask import Flask, request
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, BadPassword, TwoFactorRequired

# إعدادات التطبيق
TOKEN = '8446099371:AAEDalsTjKeVWcmYRjpUQkVDUUtH8YW3BWY'
WEBHOOK_URL = 'https://amirli.onrender.com/'

# إنشاء كائن البوت
bot = telebot.TeleBot(TOKEN)

# إنشاء تطبيق Flask
app = Flask(__name__)

# قاموس لتخزين بيانات المستخدمين المؤقتة
user_data = {}

@app.route('/')
def index():
    return "بوت الإنستغرام يعمل بشكل صحيح! 🚀"

@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    json_update = request.stream.read().decode('utf-8')
    update = telebot.types.Update.de_json(json_update)
    bot.process_new_updates([update])
    return 'OK', 200

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    user_data[chat_id] = {'step': 'waiting_username'}
    markup = telebot.types.ForceReply(selective=False)
    bot.send_message(chat_id, "مرحباً! 👋\nأرسل اسم المستخدم الخاص بحساب الإنستغرام:", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    
    if chat_id not in user_data:
        user_data[chat_id] = {'step': 'waiting_username'}
    
    if user_data[chat_id]['step'] == 'waiting_username':
        username = message.text.strip()
        user_data[chat_id]['username'] = username
        user_data[chat_id]['step'] = 'waiting_password'
        markup = telebot.types.ForceReply(selective=False)
        bot.send_message(chat_id, "حسناً! الآن أرسل كلمة المرور:", reply_markup=markup)
    
    elif user_data[chat_id]['step'] == 'waiting_password':
        password = message.text.strip()
        user_data[chat_id]['password'] = password
        
        bot.send_message(chat_id, "جاري التحقق من الحساب... ⏳")
        
        # محاولة تسجيل الدخول إلى الإنستغرام
        try:
            cl = Client()
            cl.login(user_data[chat_id]['username'], password)
            
            # الحصول على معلومات الجلسة
            session_id = cl.sessionid
            user_id = cl.user_id
            
            bot.send_message(chat_id, f"✅ تم تسجيل الدخول بنجاح!\n\n"
                                     f"📧 المستخدم: {user_data[chat_id]['username']}\n"
                                     f"🆔 Session ID: `{session_id}`\n"
                                     f"👤 User ID: `{user_id}`", parse_mode='Markdown')
            
            # مسح البيانات المؤقتة
            del user_data[chat_id]
            
        except TwoFactorRequired:
            user_data[chat_id]['step'] = 'waiting_2fa'
            markup = telebot.types.ForceReply(selective=False)
            bot.send_message(chat_id, "حسابك يستخدم التحقق بخطوتين. أرسل الرمز:", reply_markup=markup)
        
        except BadPassword:
            bot.send_message(chat_id, "❌ كلمة المرور خاطئة. أعد المحاولة باستخدام /start")
            del user_data[chat_id]
        
        except LoginRequired:
            bot.send_message(chat_id, "❌ فشل تسجيل الدخول. يرجى التحقق من البيانات والمحاولة مرة أخرى باستخدام /start")
            del user_data[chat_id]
        
        except Exception as e:
            bot.send_message(chat_id, f"❌ حدث خطأ: {str(e)}\nيرجى المحاولة مرة أخرى باستخدام /start")
            del user_data[chat_id]
    
    elif user_data[chat_id]['step'] == 'waiting_2fa':
        try:
            code = message.text.strip()
            cl = Client()
            cl.login(user_data[chat_id]['username'], user_data[chat_id]['password'], verification_code=code)
            
            session_id = cl.sessionid
            user_id = cl.user_id
            
            bot.send_message(chat_id, f"✅ تم تسجيل الدخول بنجاح!\n\n"
                                     f"📧 المستخدم: {user_data[chat_id]['username']}\n"
                                     f"🆔 Session ID: `{session_id}`\n"
                                     f"👤 User ID: `{user_id}`", parse_mode='Markdown')
            
            del user_data[chat_id]
            
        except Exception as e:
            bot.send_message(chat_id, f"❌ فشل التحقق: {str(e)}\nأعد المحاولة باستخدام /start")
            del user_data[chat_id]

if __name__ == '__main__':
    # إزالة ويب هوك السابق (إذا存在)
    bot.remove_webhook()
    
    # تعيين ويب هوك جديد
    bot.set_webhook(url=WEBHOOK_URL + TOKEN)
    
    # تشغيل التطبيق
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))