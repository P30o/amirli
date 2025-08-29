import requests
import telebot
import threading
import logging
from flask import Flask, request, jsonify
import os
import time
import json
import re
from datetime import datetime

# إعدادات التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# تهيئة Flask و Telebot
app = Flask(__name__)

# التوكن الخاص بالبوت - ضع توكنك هنا
TOKEN = "5838783352:AAGBJSOdnVlOdvKhbtS8fVnSaz4nhDOzDqU"
WEBHOOK_URL = "https://amirli.onrender.com/webhook"
bot = telebot.TeleBot(TOKEN, threaded=False)

# تخزين بيانات المستخدمين
user_data = {}

def get_asia_cell_balance(phone_number):
    """
    فحص رصيد اتصالات العراق (آسيا سيل)
    """
    try:
        url = "https://www.asia-cell.com/api/balance"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "ar,en-US;q=0.7,en;q=0.3",
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/json",
            "Origin": "https://www.asia-cell.com",
            "Connection": "keep-alive",
            "Referer": "https://www.asia-cell.com/ar/login",
        }
        
        payload = {
            "msisdn": phone_number
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return {"error": f"فشل الاتصال بالخادم: {response.status_code}"}
            
    except Exception as e:
        return {"error": f"حدث خطأ: {str(e)}"}

def get_asia_cell_offers(phone_number):
    """
    الحصول على الباقات والعروض المتاحة لرقم اتصالات
    """
    try:
        url = "https://www.asia-cell.com/api/offers"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "ar,en-US;q=0.7,en;q=0.3",
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/json",
            "Origin": "https://www.asia-cell.com",
            "Connection": "keep-alive",
            "Referer": "https://www.asia-cell.com/ar/login",
        }
        
        payload = {
            "msisdn": phone_number
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return {"error": f"فشل الاتصال بالخادم: {response.status_code}"}
            
    except Exception as e:
        return {"error": f"حدث خطأ: {str(e)}"}

def format_balance_response(data):
    """
    تنسيق استجابة الرصيد بشكل جميل
    """
    if "error" in data:
        return f"❌ {data['error']}"
    
    formatted_text = "📊 **معلومات الرصيد لاتصالات العراق**\n\n"
    
    if "balance" in data:
        formatted_text += f"💰 **الرصيد الحالي:** {data['balance']} دينار\n"
    
    if "validity" in data:
        formatted_text += f"⏰ **صلاحية الرصيد:** {data['validity']}\n"
    
    if "package" in data:
        formatted_text += f"📦 **الباقة الحالية:** {data['package']}\n"
    
    if "data_balance" in data:
        formatted_text += f"🌐 **رصيد الإنترنت:** {data['data_balance']}\n"
    
    if "last_recharge" in data:
        formatted_text += f"🔄 **آخر شحن:** {data['last_recharge']}\n"
    
    formatted_text += "\n📡 *المعلومات من نظام اتصالات العراق*"
    
    return formatted_text

def format_offers_response(data):
    """
    تنسيق استجابة العروض بشكل جميل
    """
    if "error" in data:
        return f"❌ {data['error']}"
    
    if "offers" not in data or not data["offers"]:
        return "⚠️ لا توجد عروض متاحة حالياً لرقمك"
    
    formatted_text = "🎁 **العروض والباقات المتاحة لرقمك**\n\n"
    
    for i, offer in enumerate(data["offers"][:5], 1):  # عرض أول 5 عروض فقط
        formatted_text += f"{i}. **{offer.get('name', 'عرض')}**\n"
        
        if "price" in offer:
            formatted_text += f"   💰 السعر: {offer['price']} دينار\n"
        
        if "validity" in offer:
            formatted_text += f"   ⏰ الصلاحية: {offer['validity']}\n"
        
        if "description" in offer:
            formatted_text += f"   📝 الوصف: {offer['description']}\n"
        
        formatted_text += "\n"
    
    formatted_text += "💡 *لتفعيل أي عرض، اتصل على الرقم المختصر المذكور في الوصف*"
    
    return formatted_text

def asiacell_check_thread(chat_id, phone_number, check_type):
    """
    عملية فحص الرصيد أو العروض في خيط منفصل
    """
    try:
        if check_type == "balance":
            bot.send_message(chat_id, "⏳ جاري فحص الرصيد...")
            result = get_asia_cell_balance(phone_number)
            response_text = format_balance_response(result)
        else:
            bot.send_message(chat_id, "⏳ جاري جلب العروض المتاحة...")
            result = get_asia_cell_offers(phone_number)
            response_text = format_offers_response(result)
        
        bot.send_message(chat_id, response_text, parse_mode="Markdown")
            
    except Exception as e:
        logger.error(f"Error in asiacell thread: {e}")
        bot.send_message(chat_id, "❌ حدث خطأ أثناء المعالجة. حاول مرة أخرى.")
    
    finally:
        # تنظيف حالة المستخدم
        if chat_id in user_data:
            user_data.pop(chat_id)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """
    معالج أمر /start
    """
    try:
        chat_id = message.chat.id
        
        # إنشاء واجهة بالأزرار
        markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        balance_btn = telebot.types.KeyboardButton("💰 فحص الرصيد")
        offers_btn = telebot.types.KeyboardButton("🎁 العروض المتاحة")
        help_btn = telebot.types.KeyboardButton("❓ المساعدة")
        markup.add(balance_btn, offers_btn, help_btn)
        
        welcome_text = """
        🌐 *أهلاً بك في بوت اتصالات العراق*

        📱 يمكنك من خلال هذا البوت:
        • فحص رصيدك في اتصالات العراق
        • الاطلاع على العروض والباقات المتاحة
        • استقبال إشعارات العروض الجديدة

        🔢 *أرسل رقمك الاّن* (مثال: 07701234567) 
        أو اختر أحد الخيارات من الأسفل
        """
        
        bot.send_message(
            chat_id, 
            welcome_text, 
            parse_mode="Markdown",
            reply_markup=markup
        )
        
    except Exception as e:
        logger.error(f"Error in start handler: {e}")

@bot.message_handler(func=lambda message: message.text in ["💰 فحص الرصيد", "🎁 العروض المتاحة", "❓ المساعدة"])
def handle_buttons(message):
    """
    معالج الأزرار الرئيسية
    """
    try:
        chat_id = message.chat.id
        
        if message.text == "💰 فحص الرصيد":
            if chat_id in user_data and "phone" in user_data[chat_id]:
                # بدء فحص الرصيد إذا كان الرقم محفوظاً
                thread = threading.Thread(
                    target=asiacell_check_thread, 
                    args=(chat_id, user_data[chat_id]["phone"], "balance")
                )
                thread.daemon = True
                thread.start()
            else:
                user_data[chat_id] = {"action": "balance"}
                bot.send_message(chat_id, "📱 أرسل رقم اتصالات العراق الخاص بك (مثال: 07701234567)")
        
        elif message.text == "🎁 العروض المتاحة":
            if chat_id in user_data and "phone" in user_data[chat_id]:
                # بدء جلب العروض إذا كان الرقم محفوظاً
                thread = threading.Thread(
                    target=asiacell_check_thread, 
                    args=(chat_id, user_data[chat_id]["phone"], "offers")
                )
                thread.daemon = True
                thread.start()
            else:
                user_data[chat_id] = {"action": "offers"}
                bot.send_message(chat_id, "📱 أرسل رقم اتصالات العراق الخاص بك (مثال: 07701234567)")
        
        elif message.text == "❓ المساعدة":
            help_text = """
            ❓ *كيفية استخدام البوت*
            
            1. أرسل رقم اتصالات العراق الخاص بك (مثال: 07701234567)
            2. اختر "فحص الرصيد" أو "العروض المتاحة"
            3. استلم معلوماتك فوراً
            
            📞 *للدعم الفني:* 
            تواصل مع المطور على @اسم_المطور
            
            🔒 *ملاحظة:* 
            لا يتم حفظ أي بيانات شخصية، الجميع محمي
            """
            bot.send_message(chat_id, help_text, parse_mode="Markdown")
            
    except Exception as e:
        logger.error(f"Error in buttons handler: {e}")

@bot.message_handler(func=lambda message: re.match(r'^07[0-9]{9}$', message.text.strip()))
def handle_phone_number(message):
    """
    معالج أرقام الهواتف
    """
    try:
        chat_id = message.chat.id
        phone_number = message.text.strip()
        
        # حفظ رقم الهاتف
        if chat_id not in user_data:
            user_data[chat_id] = {}
        
        user_data[chat_id]["phone"] = phone_number
        
        # إذا كان هناك إجراء محدد، تنفيذه
        if "action" in user_data[chat_id]:
            action = user_data[chat_id]["action"]
            
            if action == "balance":
                thread = threading.Thread(
                    target=asiacell_check_thread, 
                    args=(chat_id, phone_number, "balance")
                )
                thread.daemon = True
                thread.start()
            elif action == "offers":
                thread = threading.Thread(
                    target=asiacell_check_thread, 
                    args=(chat_id, phone_number, "offers")
                )
                thread.daemon = True
                thread.start()
            else:
                # إذا لم يكن هناك إجراء محدد، عرض الخيارات
                markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
                balance_btn = telebot.types.KeyboardButton("💰 فحص الرصيد")
                offers_btn = telebot.types.KeyboardButton("🎁 العروض المتاحة")
                markup.add(balance_btn, offers_btn)
                
                bot.send_message(
                    chat_id, 
                    f"✅ تم حفظ رقمك: {phone_number}\n\nاختر ما تريد القيام به:",
                    reply_markup=markup
                )
        else:
            # إذا لم يكن هناك إجراء محدد، عرض الخيارات
            markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
            balance_btn = telebot.types.KeyboardButton("💰 فحص الرصيد")
            offers_btn = telebot.types.KeyboardButton("🎁 العروض المتاحة")
            markup.add(balance_btn, offers_btn)
            
            bot.send_message(
                chat_id, 
                f"✅ تم حفظ رقمك: {phone_number}\n\nاختر ما تريد القيام به:",
                reply_markup=markup
            )
            
    except Exception as e:
        logger.error(f"Error in phone handler: {e}")

@bot.message_handler(func=lambda message: True)
def handle_other_messages(message):
    """
    معالج الرسائل الأخرى
    """
    try:
        chat_id = message.chat.id
        text = message.text.strip()
        
        if not re.match(r'^07[0-9]{9}$', text):
            bot.send_message(
                chat_id, 
                "📛 الرقم غير صحيح. يرجى إرسال رقم اتصالات العراق بصيغة صحيحة (مثال: 07701234567)"
            )
            
    except Exception as e:
        logger.error(f"Error in other messages handler: {e}")

# Routes for Flask
@app.route('/')
def home():
    return jsonify({"status": "AsiaCell Bot is Running!"})

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        return 'Invalid content type', 403

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    s = bot.set_webhook(url=WEBHOOK_URL)
    if s:
        return jsonify({"status": "Webhook setup successfully"})
    else:
        return jsonify({"status": "Webhook setup failed"})

if __name__ == '__main__':
    # إعداد الويب هوك
    bot.remove_webhook()
    time.sleep(1)
    bot.set_webhook(url=WEBHOOK_URL)
    
    # تشغيل التطبيق
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)