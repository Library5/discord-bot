# Discord Bot - Vortex 🤖

بوت ديسكورد إداري متقدم يتضمن أوامر جيفاوي وأوامر إدارية شاملة.

## الميزات ✨

### أوامر إدارية:
- **!kick** - طرد عضو من السيرفر
- **!ban** - حظر عضو من السيرفر  
- **!mute** - إسكات عضو
- **!unmute** - إلغاء إسكات عضو
- **!clear** - حذف رسائل من القناة

### أوامر جيفاوي:
- **!giveaway (المدة) (الفائزين) (الجائزة)** - إنشاء جائزة جديدة
- **!endgiveaway (message_id)** - إنهاء جائزة يدوياً

### أوامر خاصة:
- **/status (الحالة)** - تغيير ستاتيوس البوت (صاحب البوت فقط)

## التثبيت 📦

### 1. استنساخ المشروع
```bash
git clone https://github.com/Library5/discord-bot.git
cd discord-bot
```

### 2. تثبيت المتطلبات
```bash
pip install -r requirements.txt
```

### 3. إعداد متغيرات البيئة
```bash
cp .env.example .env
```

ثم عدل `.env` وأضف توكن البوت:
```
DISCORD_TOKEN=your_bot_token_here
BOT_PREFIX=!
ADMIN_ROLE=Admin
```

### 4. تشغيل البوت
```bash
python main.py
```

## متطلبات السيرفر 📋

- رول باسم "Admin" للأوامر الإدارية
- صلاحيات الإدارة للبوت
- تفعيل Message Content Intent في Developer Portal

## أمثلة الاستخدام 💡

### إنشاء جائزة:
```
!giveaway 3600 2 Nitro Classic
```
هذا ينشئ جائزة لمدة ساعة واحدة برائزين.

### طرد عضو:
```
!kick @user Spam
```

### إسكات عضو:
```
!mute @user Inappropriate content
```

### حذف رسائل:
```
!clear 50
```

### تغيير الستاتيوس (صاحب البوت فقط):
```
/status Playing Vortex 🎮
```

## البنية 📁

```
discord-bot/
├── main.py              # ملف البوت الرئيسي
├── config.py            # الإعدادات
├── requirements.txt     # المكتبات المطلوبة
├── .env.example         # مثال متغيرات البيئة
├── README.md            # التوثيق
└── cogs/
    ├── __init__.py      # حزمة Cogs
    ├── admin.py         # أوامر إدارية
    ├── giveaway.py      # أوامر جيفاوي
    └── owner.py         # أوامر خاصة بصاحب البوت
```

## المتطلبات 🔧

- Python 3.8+
- discord.py 2.3.2
- python-dotenv 1.0.0

## الترخيص 📄

حقوق النشر © 2024 g_8ia - جميع الحقوق محفوظة

## المساهمة 🤝

يمكن فقط لصاحب البوت إجراء التعديلات الرئيسية.
