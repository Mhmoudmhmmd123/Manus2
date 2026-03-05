#!/usr/bin/env python3
import os
import re
import time
import json
import threading
from datetime import datetime

from config import Config
from database.db_manager import DatabaseManager
from scrapers.scraper_manager import ScraperManager
from downloader.video_downloader import VideoDownloader
from downloader.compressor import VideoCompressor
from whatsapp.wa_client import WhatsAppClient
from utils.helpers import clean_filename, format_size, cleanup_old
from keep_alive import BotKeeper

class AnimeBot:
    def __init__(self):
        print("\033[35m\n" + "="*50)
        print("  🎬 Anime WhatsApp Bot v3.0")
        print("="*50 + "\033[0m\n")
        
        # تهيئة المكونات
        self.db = DatabaseManager()
        print("  ✅ database")
        
        self.scrapers = ScraperManager()
        print("  ✅ scraper")
        
        self.dl = VideoDownloader()
        print("  ✅ downloader")
        
        self.comp = VideoCompressor()
        print("  ✅ compressor")
        
        self.wa = WhatsAppClient(self.db)
        print("  ✅ whatsapp")
        
        # تنظيف الملفات القديمة
        cleanup_old(Config.DOWNLOAD_DIR)
        cleanup_old(Config.COMPRESSED_DIR)
        
        # نظام الإبقاء على البوت نشطاً
        self.keeper = BotKeeper(self)
        
        print("\n" + "="*50)

    def start(self):
        """بدء تشغيل البوت"""
        print("\n🚀 Starting WhatsApp Bot...\n")
        
        # تهيئة المتصفح
        self.wa.init_browser()
        
        # انتظار تسجيل الدخول
        if not self.wa.wait_login():
            print("❌ فشل تسجيل الدخول!")
            return
        
        # بدء الاستماع للرسائل في خيط منفصل
        print("👂 بدء الاستماع للرسائل...")
        listener_thread = threading.Thread(
            target=self.wa.listen, 
            args=(self.on_msg,), 
            name="WhatsAppListener",
            daemon=True
        )
        listener_thread.start()
        
        # إبقاء البوت نشطاً
        self.keeper.keep_alive()

    def on_msg(self, msg):
        """معالجة الرسائل الواردة"""
        ph = msg.get("phone", "unknown")
        text = msg.get("text", "").strip()
        
        if not text or ph == "unknown":
            return
        
        # الحصول على بيانات المستخدم
        user = self.db.get_or_create_user(ph)
        state = self.db.get_state(ph)
        
        # تسجيل الرسالة
        self.db.log("info", f"{ph}: {text}", ph)
        print(f"📩 {ph}: {text}")
        
        try:
            tl = text.lower().strip()
            
            # أوامر النظام
            if tl in ["start", "/start", "ابدأ", "بداية", "hi", "مرحبا", "السلام عليكم"]:
                self.cmd_start(ph)
            
            elif tl in ["help", "/help", "مساعدة", "أوامر", "المساعدة"]:
                self.cmd_help(ph)
            
            elif tl in ["sites", "/sites", "المواقع", "مواقع", "المواقع المتاحة"]:
                self.cmd_sites(ph)
            
            elif tl in ["settings", "/settings", "الاعدادات", "الإعدادات", "اعدادات"]:
                self.cmd_settings(ph, user)
            
            elif tl in ["cancel", "/cancel", "إلغاء", "الغاء", "رجوع", "الغاء الأمر"]:
                self.db.clear_state(ph)
                self.wa.send_msg(ph, "✅ تم إلغاء العملية الحالية\nأرسل اسم أنمي للبحث")
            
            elif re.match(r"^(موقع|site)\s+(\d+)$", tl):
                site_num = int(re.search(r"(\d+)", text).group(1))
                self.cmd_site(ph, site_num)
            
            elif re.match(r"^(جودة|quality)\s+(\S+)$", tl):
                quality = text.split()[-1]
                self.cmd_quality(ph, quality)
            
            elif re.match(r"^(سيرفر|server)\s+(\S+)$", tl):
                server = text.split()[-1]
                self.cmd_server(ph, server)
            
            elif text.strip().isdigit():
                # رقم - اختيار من قائمة
                num = int(text)
                self.handle_num(ph, num, state, user)
            
            elif tl.startswith(("بحث ", "ابحث ", "search ")):
                # أمر بحث صريح
                query = text.split(maxsplit=1)[1] if " " in text else ""
                if query:
                    self.cmd_search(ph, query, user)
            
            elif len(text) >= 2:
                # أي نص آخر يعتبر بحثاً
                self.cmd_search(ph, text, user)
            
            else:
                self.wa.send_msg(ph, "❓ أمر غير معروف\nأرسل *مساعدة* لعرض الأوامر")
                
        except Exception as e:
            print(f"❌ خطأ في معالجة الرسالة: {e}")
            import traceback
            traceback.print_exc()
            self.wa.send_msg(ph, f"❌ حدث خطأ: {str(e)[:100]}")

    def cmd_start(self, ph):
        """أمر البدء"""
        self.db.clear_state(ph)
        self.wa.send_msg(ph, 
            "🎬 *مرحباً في بوت الأنمي!*\n\n"
            "✅ 50+ موقع مدعوم\n"
            "✅ تحميل حلقات الأنمي\n"
            "✅ إرسال مباشر على واتساب\n\n"
            "⚡ *أرسل اسم أنمي للبحث*\n"
            "📝 *المواقع* - عرض المواقع المتاحة\n"
            "📝 *مساعدة* - عرض الأوامر\n"
            "📝 *الاعدادات* - إعداداتك"
        )

    def cmd_help(self, ph):
        """أمر المساعدة"""
        self.wa.send_msg(ph,
            "📖 *الأوامر المتاحة:*\n\n"
            "🔍 *اسم الأنمي* - بحث عن أنمي\n"
            "🌐 *موقع [رقم]* - اختيار موقع\n"
            "📊 *جودة [الاسم]* - اختيار جودة\n"
            "🖥️ *سيرفر [الاسم]* - اختيار سيرفر\n"
            "⚙️ *الاعدادات* - عرض إعداداتك\n"
            "↩️ *إلغاء* - إلغاء العملية الحالية\n\n"
            "✅ أرسل اسم أنمي للبدء"
        )

    def cmd_sites(self, ph):
        """عرض المواقع المتاحة"""
        sites_text = self.scrapers.sites_text()
        self.wa.send_msg(ph, 
            sites_text + "\n\n📌 *موقع [رقم]* لاختيار موقع"
        )

    def cmd_settings(self, ph, user):
        """عرض الإعدادات"""
        site = Config.SITES.get(user["preferred_site"], {})
        self.wa.send_msg(ph,
            f"⚙️ *إعداداتك*\n\n"
            f"🌐 الموقع: *{site.get('name', '?')}*\n"
            f"📊 الجودة: *{user['preferred_quality']}*\n"
            f"🖥️ السيرفر: *{user['preferred_server']}*\n"
            f"📥 التحميلات: *{user['total_downloads']}*\n\n"
            f"لتغيير:\n"
            f"• *موقع [رقم]*\n"
            f"• *جودة [الاسم]*\n"
            f"• *سيرفر [الاسم]*"
        )

    def cmd_site(self, ph, site_num):
        """تغيير الموقع المفضل"""
        if site_num in Config.SITES:
            self.db.update_user(ph, preferred_site=site_num)
            self.wa.send_msg(ph, 
                f"✅ تم اختيار *{Config.SITES[site_num]['name']}*\n\n"
                f"أرسل اسم أنمي للبحث!"
            )
        else:
            self.wa.send_msg(ph, "❌ رقم موقع غير صحيح!")

    def cmd_quality(self, ph, quality):
        """تغيير الجودة المفضلة"""
        if quality in Config.QUALITIES:
            self.db.update_user(ph, preferred_quality=quality)
            self.wa.send_msg(ph, f"✅ تم اختيار الجودة: *{quality}*")
        else:
            self.wa.send_msg(ph, 
                f"❌ الجودات المتاحة: {', '.join(Config.QUALITIES)}"
            )

    def cmd_server(self, ph, server):
        """تغيير السيرفر المفضل"""
        if server.lower() in [x.lower() for x in Config.SERVERS]:
            self.db.update_user(ph, preferred_server=server.lower())
            self.wa.send_msg(ph, f"✅ تم اختيار السيرفر: *{server}*")
        else:
            self.wa.send_msg(ph, 
                f"❌ السيرفرات المتاحة: {', '.join(Config.SERVERS[:8])}"
            )

    def cmd_search(self, ph, query, user):
        """البحث عن أنمي"""
        self.db.clear_state(ph)
        self.wa.send_msg(ph, f"🔍 جاري البحث عن *{query}*...")
        
        results = self.scrapers.search(query, user["preferred_site"])
        
        if not results:
            self.wa.send_msg(ph, "😔 لا توجد نتائج! جرب اسماً آخر")
            return
        
        results = results[:15]  # حد أقصى 15 نتيجة
        self.db.set_state(ph, {"step": "anime", "results": results})
        
        msg = f"🎬 *نتائج البحث عن {query}:*\n\n"
        for i, anime in enumerate(results, 1):
            title = anime.get('title_ar') or anime.get('title_en', '?')
            site = anime.get('site', '')
            msg += f"*{i}.* {title} 🌐{site}\n"
        
        self.wa.send_msg(ph, msg + "\n📌 أرسل رقم الأنمي")

    def handle_num(self, ph, num, state, user):
        """معالجة الأرقام المرسلة"""
        step = state.get("step", "")
        
        if step == "anime":
            self.sel_anime(ph, num, state, user)
        elif step == "season":
            self.sel_season(ph, num, state, user)
        elif step == "episode":
            self.sel_episode(ph, num, state, user)
        elif step == "quality":
            self.sel_quality(ph, num, state, user)
        elif step == "server":
            self.sel_server(ph, num, state, user)
        else:
            self.wa.send_msg(ph, "❓ أرسل اسم أنمي أولاً")

    def sel_anime(self, ph, num, state, user):
        """اختيار أنمي من النتائج"""
        results = state.get("results", [])
        
        if not (1 <= num <= len(results)):
            self.wa.send_msg(ph, "❌ رقم غير صحيح!")
            return
        
        anime = results[num - 1]
        self.wa.send_msg(ph, f"⏳ جلب بيانات *{anime.get('title_ar', '...')}*...")
        
        scraper = self.scrapers.get(user["preferred_site"])
        if not scraper:
            self.wa.send_msg(ph, "❌ الموقع غير مدعوم!")
            return
        
        try:
            seasons = scraper.get_seasons(anime.get("url", ""))
        except Exception as e:
            print(f"خطأ في جلب المواسم: {e}")
            seasons = [{"num": 1, "title": "الموسم 1", "url": anime.get("url", "")}]
        
        if len(seasons) > 1:
            self.db.set_state(ph, {"step": "season", "anime": anime, "seasons": seasons})
            msg = f"📺 *{anime.get('title_ar', '')}*\n\n"
            for i, s in enumerate(seasons, 1):
                msg += f"*{i}.* {s.get('title', f'الموسم {i}')}\n"
            self.wa.send_msg(ph, msg + "\n📌 أرسل رقم الموسم")
        else:
            url = seasons[0]["url"] if seasons else anime.get("url", "")
            self.show_eps(ph, anime, url, 1, user)

    def sel_season(self, ph, num, state, user):
        """اختيار موسم"""
        seasons = state.get("seasons", [])
        
        if not (1 <= num <= len(seasons)):
            self.wa.send_msg(ph, "❌ رقم غير صحيح!")
            return
        
        self.show_eps(ph, state["anime"], seasons[num - 1]["url"], num, user)

    def show_eps(self, ph, anime, url, season_num, user):
        """عرض الحلقات"""
        self.wa.send_msg(ph, "⏳ جلب الحلقات...")
        
        scraper = self.scrapers.get(user["preferred_site"])
        if not scraper:
            return
        
        try:
            episodes = scraper.get_episodes(url)
        except Exception as e:
            print(f"خطأ في جلب الحلقات: {e}")
            episodes = []
        
        if not episodes:
            self.wa.send_msg(ph, "😔 لا توجد حلقات!")
            return
        
        self.db.set_state(ph, {
            "step": "episode", 
            "anime": anime, 
            "episodes": episodes, 
            "season": season_num
        })
        
        msg = f"📺 *{anime.get('title_ar', '')}* الموسم {season_num}\n({len(episodes)} حلقة)\n\n"
        for i, ep in enumerate(episodes, 1):
            msg += f"*{i}.* الحلقة {ep.get('num', i)}\n"
            
            if i % 40 == 0 and i < len(episodes):
                self.wa.send_msg(ph, msg)
                msg = ""
                time.sleep(1)
        
        self.wa.send_msg(ph, msg + "\n📌 أرسل رقم الحلقة")

    def sel_episode(self, ph, num, state, user):
        """اختيار حلقة"""
        episodes = state.get("episodes", [])
        
        if not (1 <= num <= len(episodes)):
            self.wa.send_msg(ph, "❌ رقم غير صحيح!")
            return
        
        ep = episodes[num - 1]
        anime = state["anime"]
        season_num = state.get("season", 1)
        
        self.wa.send_msg(ph, f"⏳ جلب روابط الحلقة {ep.get('num', num)}...")
        
        scraper = self.scrapers.get(user["preferred_site"])
        if not scraper:
            return
        
        try:
            links = scraper.get_download_links(ep.get("url", ""))
        except Exception as e:
            print(f"خطأ في جلب الروابط: {e}")
            links = {}
        
        if not links:
            self.wa.send_msg(ph, "😔 لا توجد روابط تحميل!")
            return
        
        qualities = list(links.keys())
        
        if len(qualities) > 1:
            self.db.set_state(ph, {
                "step": "quality", 
                "anime": anime, 
                "episode": ep, 
                "season": season_num, 
                "links": links, 
                "qualities": qualities
            })
            msg = "📊 *اختر الجودة:*\n\n"
            for i, q in enumerate(qualities, 1):
                msg += f"*{i}.* {q} ({len(links[q])} سيرفر)\n"
            self.wa.send_msg(ph, msg + "\n📌 أرسل رقم الجودة")
        else:
            q = qualities[0]
            servers = list(links[q].keys())
            
            if len(servers) > 1:
                self.db.set_state(ph, {
                    "step": "server", 
                    "anime": anime, 
                    "episode": ep, 
                    "season": season_num, 
                    "links": links, 
                    "quality": q, 
                    "servers": servers
                })
                msg = f"🖥️ *اختر السيرفر ({q}):*\n\n"
                for i, sv in enumerate(servers, 1):
                    msg += f"*{i}.* {sv}\n"
                self.wa.send_msg(ph, msg + "\n📌 أرسل رقم السيرفر")
            else:
                self.begin_download(ph, anime, ep, season_num, links, q, servers[0], user)

    def sel_quality(self, ph, num, state, user):
        """اختيار جودة"""
        qualities = state.get("qualities", [])
        
        if not (1 <= num <= len(qualities)):
            self.wa.send_msg(ph, "❌ رقم غير صحيح!")
            return
        
        q = qualities[num - 1]
        links = state["links"]
        servers = list(links[q].keys())
        
        if len(servers) > 1:
            self.db.set_state(ph, {
                "step": "server", 
                "anime": state["anime"], 
                "episode": state["episode"], 
                "season": state["season"], 
                "links": links, 
                "quality": q, 
                "servers": servers
            })
            msg = f"🖥️ *اختر السيرفر ({q}):*\n\n"
            for i, sv in enumerate(servers, 1):
                msg += f"*{i}.* {sv}\n"
            self.wa.send_msg(ph, msg + "\n📌 أرسل رقم السيرفر")
        else:
            self.begin_download(ph, state["anime"], state["episode"], state["season"], links, q, servers[0], user)

    def sel_server(self, ph, num, state, user):
        """اختيار سيرفر"""
        servers = state.get("servers", [])
        
        if not (1 <= num <= len(servers)):
            self.wa.send_msg(ph, "❌ رقم غير صحيح!")
            return
        
        q = state.get("quality", list(state["links"].keys())[0])
        self.begin_download(ph, state["anime"], state["episode"], state["season"], state["links"], q, servers[num - 1], user)

    def begin_download(self, ph, anime, episode, season_num, links, quality, server, user):
        """بدء التحميل في خيط منفصل"""
        self.db.clear_state(ph)
        download_thread = threading.Thread(
            target=self.download_video, 
            args=(ph, anime, episode, season_num, links, quality, server, user),
            daemon=True
        )
        download_thread.start()

    def download_video(self, ph, anime, episode, season_num, links, quality, server, user):
        """تحميل الفيديو وإرساله"""
        title = anime.get("title_ar") or anime.get("title_en", "anime")
        ep_num = episode.get("num", 0)
        
        try:
            # حفظ سجل التحميل
            download_id = self.db.save_download({
                "phone": ph,
                "anime_title": title,
                "ep_num": ep_num,
                "season_num": season_num,
                "site": Config.SITES.get(user["preferred_site"], {}).get("name", ""),
                "quality": quality,
                "server": server
            })
            
            # الحصول على رابط التحميل
            download_url = links.get(quality, {}).get(server, "")
            if not download_url:
                # بحث بديل عن أي رابط
                for q, servers in links.items():
                    for s, url in servers.items():
                        download_url = url
                        break
                    if download_url:
                        break
            
            if not download_url:
                self.wa.send_msg(ph, "❌ لا يوجد رابط تحميل!")
                return
            
            self.wa.send_msg(ph, 
                f"⬇️ *جاري التحميل...*\n"
                f"🎬 {title}\n"
                f"📺 S{season_num}E{int(ep_num)} | {quality} | {server}"
            )
            
            # محاولة الحصول على رابط مباشر
            scraper = self.scrapers.get(user["preferred_site"])
            if scraper:
                try:
                    direct_url = scraper.get_direct_link(download_url, quality)
                    if direct_url:
                        download_url = direct_url
                except:
                    pass
            
            # اسم الملف
            filename = clean_filename(f"{title}_S{season_num}E{int(ep_num)}_{quality}.mp4")
            
            # دالة تقدم التحميل
            def progress_callback(percent, speed, downloaded, total):
                if int(percent) in [25, 50, 75]:
                    self.wa.send_msg(ph, f"⬇️ {percent:.0f}% ({format_size(int(speed))}/s)")
            
            # التحميل
            result = self.dl.download(download_url, filename, progress_callback)
            
            if not result["success"]:
                # محاولة بديلة
                self.wa.send_msg(ph, "🔄 محاولة تحميل بديلة...")
                result = self.dl.download_ytdlp(download_url, filename, quality)
            
            if not result["success"]:
                self.db.update_download(download_id, status="failed", error_msg=result.get("error", ""))
                self.wa.send_msg(ph, f"❌ فشل التحميل!\n{result.get('error', '')}\nجرب سيرفر أو موقع آخر")
                return
            
            filepath = result["filepath"]
            size_mb = result["size_mb"]
            
            self.db.update_download(download_id, status="downloaded", file_size_mb=round(size_mb, 2))
            self.wa.send_msg(ph, f"✅ تم التحميل ({size_mb:.1f}MB)\n🔄 جاري التجهيز للإرسال...")
            
            # ضغط الفيديو
            compressed = self.comp.compress_for_wa(filepath)
            
            if not compressed["success"]:
                self.wa.send_msg(ph, f"❌ فشل الضغط: {compressed.get('error', '')}")
                self.cleanup_files(filepath)
                return
            
            # إرسال الفيديو
            if compressed.get("split"):
                parts = compressed["parts"]
                self.wa.send_msg(ph, f"📦 تم تقسيم الفيديو إلى {len(parts)} أجزاء")
                for p in parts:
                    self.wa.send_file(ph, p["path"], 
                        f"🎬 {title} S{season_num}E{int(ep_num)} جزء {p['part']}/{len(parts)}")
                    time.sleep(3)
            else:
                output_path = compressed["output"]
                output_size = compressed.get("output_mb", 0)
                
                self.wa.send_msg(ph, "📤 جاري الإرسال...")
                if self.wa.send_file(ph, output_path, 
                    f"🎬 *{title}*\n📺 S{season_num}E{int(ep_num)} | {quality} | {output_size:.1f}MB"):
                    
                    self.db.update_download(download_id, status="completed", 
                        compressed_size_mb=round(output_size, 2),
                        completed_at=datetime.now().isoformat(), 
                        sent_at=datetime.now().isoformat())
                    
                    self.db.update_user(ph, total_downloads=user["total_downloads"] + 1)
                    
                    self.wa.send_msg(ph, "✅ *تم الإرسال بنجاح!*\n🔍 أرسل اسم أنمي آخر")
                else:
                    self.wa.send_msg(ph, "❌ فشل إرسال الفيديو")
            
            # تنظيف الملفات
            self.cleanup_files(filepath, compressed)
            
        except Exception as e:
            print(f"❌ خطأ في التحميل: {e}")
            import traceback
            traceback.print_exc()
            self.wa.send_msg(ph, f"❌ حدث خطأ: {str(e)[:100]}")

    def cleanup_files(self, filepath, compressed=None):
        """تنظيف الملفات المؤقتة"""
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
            
            if compressed:
                if compressed.get("split"):
                    for p in compressed.get("parts", []):
                        if os.path.exists(p.get("path", "")):
                            os.remove(p["path"])
                elif compressed.get("compressed"):
                    output = compressed.get("output", "")
                    if output and os.path.exists(output):
                        os.remove(output)
        except Exception as e:
            print(f"⚠️ خطأ في التنظيف: {e}")

if __name__ == "__main__":
    print("🚀 بدء تشغيل بوت الأنمي...")
    bot = AnimeBot()
    
    try:
        bot.start()
    except KeyboardInterrupt:
        print("\n👋 تم إيقاف البوت بواسطة المستخدم")
    except Exception as e:
        print(f"❌ خطأ غير متوقع: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if hasattr(bot, 'wa'):
            print("🔄 جاري إغلاق اتصال واتساب...")
            try:
                bot.wa.close()
            except:
                pass
        print("✅ تم إيقاف البوت بنجاح")
