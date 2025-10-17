from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    # دي الرسالة اللي بيشوفها UptimeRobot لما بيزور الرابط
    return "Hello! RAG Chatbot is alive!"

def run():
  # تشغيل السيرفر على الـ Host والـ Port اللي بيستخدمهم Replit
  # (0.0.0.0 و 8080 هم القيم الافتراضية)
  app.run(host='0.0.0.0', port=8080)

def keep_alive():
    # هنا بنبدأ عملية تشغيل السيرفر في خيط (Thread) منفصل
    # عشان ما يوقفش الكود الأساسي في bot.py
    t = Thread(target=run)
    t.start()
