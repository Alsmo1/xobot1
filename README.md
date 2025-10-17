🎮 XO Telegram Bot - Advanced Edition
بوت تليجرام متقدم للعبة XO (إكس-أو) مع ميزات رائعة!

✨ المميزات
🎨 6 ثيمات مختلفة
Classic (❌⭕)
Hearts (❤️💙)
Animals (🐱🐶)
Fruits (🍎🍊)
Space (🌟🌙)
Emoji (😎🤓)
⏱️ وضعين للعب
عادي: لعب بدون حدود زمنية
بالوقت: 60 ثانية لكل لاعب مع عداد تنازلي
📊 إحصائيات متقدمة
إجمالي المباريات
الانتصارات والخسارات والتعادل
نسبة الفوز
تاريخ آخر 10 مباريات
🎵 تفاعل ممتع
ستيكرز تلقائية عند الفوز/الخسارة
رسائل تشجيعية عشوائية
إشعارات ذكية
💾 حفظ تلقائي
حفظ جميع البيانات في xo_data.json
استمرارية الثيم المفضل
حفظ التاريخ الكامل
🚀 التثبيت المحلي
bash
# استنساخ المشروع
git clone <your-repo-url>
cd xo-telegram-bot

# تثبيت المتطلبات
pip install -r requirements.txt

# تشغيل البوت
python bot.py
☁️ النشر على Render.com
الخطوات:
إنشاء حساب على Render.com
اذهب إلى render.com
سجل حساب جديد
رفع الكود على GitHub
bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
إنشاء Web Service على Render
اضغط "New +" → "Web Service"
اربط حساب GitHub
اختر الـ repository
الإعدادات:
Name: xo-telegram-bot
Environment: Python 3
Build Command: pip install -r requirements.txt
Start Command: python bot.py
Plan: Free
إضافة Environment Variable (اختياري)
في إعدادات الـ Service
أضف BOT_TOKEN كـ Environment Variable
عدل الكود ليقرأ من المتغير:
python
   import os
   TOKEN = os.getenv('BOT_TOKEN', 'your-token-here')
Deploy!
اضغط "Create Web Service"
انتظر حتى ينتهي الـ deployment
البوت سيعمل 24/7! ✅
📱 الأوامر
/start - بدء اللعبة وعرض القائمة الرئيسية
اختر الوضع والثيم من الأزرار التفاعلية
🎯 طريقة اللعب
أرسل /start للبوت
اختر وضع اللعب (عادي أو بالوقت)
اضغط على المربعات للعب
حاول الحصول على 3 رموز متتالية للفوز!
🛠️ التقنيات المستخدمة
Python 3.11
python-telegram-bot 20.7
JSON لتخزين البيانات
Async/Await للأداء الأمثل
📊 هيكل البيانات
json
{
  "stats": {
    "user_id": {
      "wins": 0,
      "losses": 0,
      "draws": 0,
      "total_games": 0,
      "history": []
    }
  },
  "themes": {
    "user_id": "classic"
  }
}
🔒 الأمان
لا تشارك الـ TOKEN الخاص بك
استخدم Environment Variables في الإنتاج
راجع الـ .gitignore قبل الرفع على GitHub
🤝 المساهمة
المشروع مفتوح المصدر! يمكنك المساهمة بـ:

إضافة ميزات جديدة
إصلاح الأخطاء
تحسين الكود
ترجمة البوت
📝 الترخيص
MIT License - استخدم المشروع بحرية!

👨‍💻 المطور
تم التطوير بواسطة Alsmwal Berema Omda

📞 الدعم
إذا واجهت أي مشكلة:

افتح Issue على GitHub
راسل البوت مباشرة
راجع قسم المساعدة في البوت
🎮 استمتع باللعب!

⭐ لا تنسى عمل Star للمشروع إذا أعجبك!

"# xobot1" 
