# 🎬 Anime WhatsApp Bot

> بوت واتساب لتحميل الأنمي المترجم م�� 50+ موقع

## المميزات
- ✅ دعم 50+ موقع أنمي (عربي + إنجليزي)
- ✅ اختيار الجودة (240p - 1080p)
- ✅ اختيار سيرفر التحميل
- ✅ ضغط تلقائي بـ FFmpeg
- ✅ إرسال مباشر عب�� واتساب
- ✅ يعمل على Termux
- ✅ قاعدة بيانات SQLite
- ✅ إعادة تشغيل تلقائي

## التثبيت على Termux (أمر واحد)
```bash
bash setup.sh
```

## التثبيت اليدوي
```bash
# 1. استنساخ المشروع
git clone https://github.com/YOUR_USERNAME/anime-whatsapp-bot.git
cd anime-whatsapp-bot

# 2. تثبيت المتطلبات
pkg install -y python ffmpeg chromium build-essential libxml2 libxslt
pip install -r requirements.txt

# 3. تشغيل البوت
python main.py
```

## الأوامر
| الأمر | الوصف |
|-------|-------|
| اسم أنمي | بحث مباشر |
| المواقع | عرض المواقع |
| موقع 1 | اختيار موقع |
| جودة 720p | تغيير الجودة |
| سيرفر mp4upload | تغيير السيرفر |
| الاعدادات | عرض إعداداتك |
| إلغاء | إلغاء العملية |
| مساعدة | المساعدة |

## المواقع المدعومة (50+)
### عربية
Anime4up, WitAnime, AnimeLek, AnimeBlkom, AnimeRco, AnimeSanka, OkAnime, ShahiidAnime, AnimeCloud, XSAnime, AnimeStars, AnimeTak, Arabsama, Egyanime, Animeiat, JustAnime, AnimeMaster, AnimeDown, AnimeY, AnimeKSA, FasrHD, AnimeFlv, AnimeSail, AnimeRush, TurkAnime

### إنجليزية
GogoAnime, 9Anime, Zoro, AnimePahe, KissAnime, AnimeFreak, AnimeFlix, AnimeOwl, AnimeFox, AniWatch, KickAssAnime, AnimeDao, AnimeHeaven, AnimeSuge, AnimixPlay, Nyaa, AnimeKisa, AnimeUltima, DarkAnime, AnimeSimple, AnimeBee, YugenAnime, AllAnime, Crunchyroll, WCOStream

## البنية
```
anime-whatsapp-bot/
├── main.py              # الملف الرئيسي
├── config.py            # الإعدادات
├── setup.sh             # س��ربت التثبيت
├── run.sh               # سكربت التشغيل
├── requirements.txt     # المكتبات
├── database/
│   └── db_manager.py    # قاعدة البيانات
├── scrapers/
│   ├── base_scraper.py  # القالب الأساسي
│   ├── anime4up.py      # Anime4up
│   ├── witanime.py      # WitAnime
│   ├── gogoanime.py     # GogoAnime
│   ├── generic_scraper.py # سكرابر عا��
│   └── scraper_manager.py # المدير
├── downloader/
│   ├── video_downloader.py # التحميل
│   └── compressor.py    # الضغط
├── whatsapp/
│   └── wa_client.py     # واتساب
└── utils/
    └── helpers.py       # أدوات
```

## الترخيص
MIT License - للاستخدام الشخصي والتعليمي