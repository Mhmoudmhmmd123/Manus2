#!/usr/bin/env python3
import os, re, time, json, threading
from datetime import datetime
from config import Config
from database.db_manager import DatabaseManager
from scrapers.scraper_manager import ScraperManager
from downloader.video_downloader import VideoDownloader
from downloader.compressor import VideoCompressor
from whatsapp.wa_client import WhatsAppClient
from utils.helpers import clean_filename, format_size, cleanup_old

class AnimeBot:
    def __init__(self):
        print("\033[35m\n" + "="*50)
        print("  🎬 Anime WhatsApp Bot v3.0")
        print("="*50 + "\033[0m\n")
        self.db = DatabaseManager(); print("  ✅ database")
        self.scrapers = ScraperManager()
        self.dl = VideoDownloader(); print("  ✅ downloader")
        self.comp = VideoCompressor(); print("  ✅ compressor")
        self.wa = WhatsAppClient(self.db); print("  ✅ whatsapp")
        cleanup_old(Config.DOWNLOAD_DIR); cleanup_old(Config.COMPRESSED_DIR)

    def start(self):
        print("\n🚀 Starting...\n")
        self.wa.init_browser()
        if not self.wa.wait_login(): print("❌ Login failed!"); return
        print("\n" + "="*50 + "\n  ✅ BOT IS RUNNING!\n" + "="*50 + "\n")
        self.wa.listen(self.on_msg)

    def on_msg(self, msg):
        ph = msg["phone"]; text = msg["text"].strip()
        if not text or ph == "unknown": return
        user = self.db.get_or_create_user(ph); state = self.db.get_state(ph)
        self.db.log("info", f"{ph}: {text}", ph); print(f"📩 {ph}: {text}")
        try:
            tl = text.lower().strip()
            if tl in ["start","/start","ابدأ","بداية","hi","مرحبا"]: self.cmd_start(ph)
            elif tl in ["help","/help","مساعدة","أوامر"]: self.cmd_help(ph)
            elif tl in ["sites","/sites","المواقع","مواقع"]: self.cmd_sites(ph)
            elif tl in ["settings","/settings","الاعدادات","الإعدادات"]: self.cmd_settings(ph, user)
            elif tl in ["cancel","/cancel","إلغاء","الغاء","رجوع"]:
                self.db.clear_state(ph); self.wa.send_msg(ph, "✅ تم\nأرسل اسم أنمي")
            elif re.match(r"^(موقع|site)\s+(\d+)$", tl):
                self.cmd_site(ph, int(re.search(r"(\d+)", text).group(1)))
            elif re.match(r"^(جودة|quality)\s+(\S+)$", tl): self.cmd_quality(ph, text.split()[-1])
            elif re.match(r"^(سيرفر|server)\s+(\S+)$", tl): self.cmd_server(ph, text.split()[-1])
            elif text.strip().isdigit(): self.handle_num(ph, int(text), state, user)
            elif tl.startswith(("بحث ","ابحث ","search ")):
                q = text.split(maxsplit=1)[1] if " " in text else ""
                if q: self.cmd_search(ph, q, user)
            elif len(text) >= 2: self.cmd_search(ph, text, user)
            else: self.wa.send_msg(ph, "❓ أرسل *مساعدة*")
        except Exception as e:
            print(f"❌ {e}"); import traceback; traceback.print_exc()
            self.wa.send_msg(ph, f"❌ {e}")

    def cmd_start(self, ph):
        self.db.clear_state(ph)
        self.wa.send_msg(ph, "🎬 *مرحباً في بوت الأنمي!*\n\n50+ موقع مدعوم!\n\n⚡ أرسل اسم أنمي للبحث\n📝 *المواقع* | *مساعدة* | *الاعدادات*")

    def cmd_help(self, ph):
        self.wa.send_msg(ph, "📖 *المساعدة:*\n\n🔍 أرسل اسم أنمي\n🌐 \n📊 \n🖥️ \n↩️ *إلغاء*")

    def cmd_sites(self, ph):
        self.wa.send_msg(ph, self.scrapers.sites_text() + "\n\n📌 *موقع [رقم]*")

    def cmd_settings(self, ph, u):
        s = Config.SITES.get(u["preferred_site"], {})
        self.wa.send_msg(ph, f"⚙️ الموقع: *{s.get('name','?')}*\nالجودة: *{u['preferred_quality']}*\nالسيرفر: *{u['preferred_server']}*\nتحميلات: *{u['total_downloads']}*")

    def cmd_site(self, ph, n):
        if n in Config.SITES:
            self.db.update_user(ph, preferred_site=n)
            self.wa.send_msg(ph, f"✅ *{Config.SITES[n]['name']}*\n\nأرسل اسم أنمي!")
        else: self.wa.send_msg(ph, "❌ رقم خطأ!")

    def cmd_quality(self, ph, q):
        if q in Config.QUALITIES:
            self.db.update_user(ph, preferred_quality=q); self.wa.send_msg(ph, f"✅ {q}")
        else: self.wa.send_msg(ph, f"❌ ال��تاح: {', '.join(Config.QUALITIES)}")

    def cmd_server(self, ph, s):
        if s.lower() in [x.lower() for x in Config.SERVERS]:
            self.db.update_user(ph, preferred_server=s.lower()); self.wa.send_msg(ph, f"✅ {s}")
        else: self.wa.send_msg(ph, f"❌ المتاح: {', '.join(Config.SERVERS[:8])}")

    def cmd_search(self, ph, query, user):
        self.db.clear_state(ph); self.wa.send_msg(ph, f"🔍 *{query}*...")
        results = self.scrapers.search(query, user["preferred_site"])
        if not results: self.wa.send_msg(ph, "😔 لا نتائج!"); return
        results = results[:15]; self.db.set_state(ph, {"step": "anime", "results": results})
        msg = f"🎬 *{query}:*\n\n"
        for i, a in enumerate(results, 1):
            msg += f"*{i}.* {a.get('title_ar') or a.get('title_en','?')} 🌐{a.get('site','')}\n"
        self.wa.send_msg(ph, msg + "\n📌 أرسل الرقم")

    def handle_num(self, ph, n, state, user):
        step = state.get("step", "")
        if step == "anime": self.sel_anime(ph, n, state, user)
        elif step == "season": self.sel_season(ph, n, state, user)
        elif step == "episode": self.sel_episode(ph, n, state, user)
        elif step == "quality": self.sel_quality(ph, n, state, user)
        elif step == "server": self.sel_server(ph, n, state, user)
        else: self.wa.send_msg(ph, "❓ أرسل اسم أنمي")

    def sel_anime(self, ph, n, st, user):
        res = st.get("results", [])
        if not (1 <= n <= len(res)): self.wa.send_msg(ph, "❌!"); return
        anime = res[n-1]; self.wa.send_msg(ph, f"⏳ *{anime.get('title_ar','...')}*...")
        scraper = self.scrapers.get(user["preferred_site"])
        if not scraper: self.wa.send_msg(ph, "❌ غير مدعوم"); return
        try: seasons = scraper.get_seasons(anime.get("url", ""))
        except: seasons = [{"num": 1, "title": "ال��وسم 1", "url": anime.get("url", "")}]
        if len(seasons) > 1:
            self.db.set_state(ph, {"step": "season", "anime": anime, "seasons": seasons})
            msg = f"📺 *{anime.get('title_ar','')}*\n\n"
            for i, s in enumerate(seasons, 1): msg += f"*{i}.* {s.get('title', f'المو��م {i}')}\n"
            self.wa.send_msg(ph, msg + "\n📌 أرسل رقم الموسم")
        else:
            url = seasons[0]["url"] if seasons else anime.get("url", "")
            self.show_eps(ph, anime, url, 1, user)

    def sel_season(self, ph, n, st, user):
        ss = st.get("seasons", [])
        if not (1 <= n <= len(ss)): self.wa.send_msg(ph, "❌!"); return
        self.show_eps(ph, st["anime"], ss[n-1]["url"], n, user)

    def show_eps(self, ph, anime, url, sn, user):
        self.wa.send_msg(ph, "⏳ الحلقات...")
        scraper = self.scrapers.get(user["preferred_site"])
        if not scraper: return
        try: eps = scraper.get_episodes(url)
        except: eps = []
        if not eps: self.wa.send_msg(ph, "😔 لا حلقات!"); return
        self.db.set_state(ph, {"step": "episode", "anime": anime, "episodes": eps, "season": sn})
        msg = f"📺 *{anime.get('title_ar','')}* S{sn}\n({len(eps)} حلقة)\n\n"
        for i, ep in enumerate(eps, 1):
            msg += f"*{i}.* الحلقة {ep.get('num', i)}\n"
            if i % 40 == 0 and i < len(eps): self.wa.send_msg(ph, msg); msg = ""; time.sleep(1)
        self.wa.send_msg(ph, msg + "\n📌 أرسل رقم الحلقة")

    def sel_episode(self, ph, n, st, user):
        eps = st.get("episodes", [])
        if not (1 <= n <= len(eps)): self.wa.send_msg(ph, "❌!"); return
        ep = eps[n-1]; anime = st["anime"]; sn = st.get("season", 1)
        self.wa.send_msg(ph, f"⏳ روابط الحلقة {ep.get('num', n)}...")
        scraper = self.scrapers.get(user["preferred_site"])
        if not scraper: return
        try: links = scraper.get_download_links(ep.get("url", ""))
        except: links = {}
        if not links: self.wa.send_msg(ph, "😔 لا روابط!"); return
        qs = list(links.keys())
        if len(qs) > 1:
            self.db.set_state(ph, {"step": "quality", "anime": anime, "episode": ep, "season": sn, "links": links, "qs": qs})
            msg = "📊 *الجودات:*\n\n"
            for i, q in enumerate(qs, 1): msg += f"*{i}.* {q} ({len(links[q])} سيرفر)\n"
            self.wa.send_msg(ph, msg + "\n📌 رقم الجودة")
        else:
            q = qs[0]; svs = list(links[q].keys())
            if len(svs) > 1:
                self.db.set_state(ph, {"step": "server", "anime": anime, "episode": ep, "season": sn, "links": links, "quality": q, "svs": svs})
                msg = f"🖥️ *السيرفرات ({q}):*\n\n"
                for i, sv in enumerate(svs, 1): msg += f"*{i}.* {sv}\n"
                self.wa.send_msg(ph, msg + "\n📌 رقم السيرفر")
            else: self.begin_dl(ph, anime, ep, sn, links, q, svs[0], user)

    def sel_quality(self, ph, n, st, user):
        qs = st.get("qs", [])
        if not (1 <= n <= len(qs)): self.wa.send_msg(ph, "❌!"); return
        q = qs[n-1]; links = st["links"]; svs = list(links[q].keys())
        if len(svs) > 1:
            self.db.set_state(ph, {"step": "server", "anime": st["anime"], "episode": st["episode"], "season": st["season"], "links": links, "quality": q, "svs": svs})
            msg = f"🖥️ *السيرفرات ({q}):*\n\n"
            for i, sv in enumerate(svs, 1): msg += f"*{i}.* {sv}\n"
            self.wa.send_msg(ph, msg + "\n📌 رقم السيرفر")
        else: self.begin_dl(ph, st["anime"], st["episode"], st["season"], links, q, svs[0], user)

    def sel_server(self, ph, n, st, user):
        svs = st.get("svs", [])
        if not (1 <= n <= len(svs)): self.wa.send_msg(ph, "❌!"); return
        q = st.get("quality", list(st["links"].keys())[0])
        self.begin_dl(ph, st["anime"], st["episode"], st["season"], st["links"], q, svs[n-1], user)

    def begin_dl(self, ph, anime, ep, sn, links, q, sv, user):
        self.db.clear_state(ph)
        threading.Thread(target=self._dl, daemon=True, args=(ph, anime, ep, sn, links, q, sv, user)).start()

    def _dl(self, ph, anime, ep, sn, links, q, sv, user):
        title = anime.get("title_ar") or anime.get("title_en", "anime"); en = ep.get("num", 0)
        try:
            dl_id = self.db.save_download({"phone": ph, "anime_title": title, "ep_num": en, "season_num": sn,
                "site": Config.SITES.get(user["preferred_site"],{}).get("name",""), "quality": q, "server": sv})
            dl_url = links.get(q, {}).get(sv, "")
            if not dl_url:
                for qq, ss in links.items():
                    for s, u in ss.items(): dl_url = u; break
                    if dl_url: break
            if not dl_url: self.wa.send_msg(ph, "❌ لا رابط!"); return
            self.wa.send_msg(ph, f"⬇️ *تحميل...*\n🎬 {title}\n📺 S{sn}E{int(en)} | {q} | {sv}")
            scraper = self.scrapers.get(user["preferred_site"])
            if scraper:
                try:
                    d = scraper.get_direct_link(dl_url, q)
                    if d: dl_url = d
                except: pass
            fname = clean_filename(f"{title}_S{sn}E{int(en)}_{q}.mp4")
            def pcb(pct, speed, d, t):
                if int(pct) in [25,50,75]: self.wa.send_msg(ph, f"⬇️ {pct:.0f}% ({format_size(int(speed))}/s)")
            result = self.dl.download(dl_url, fname, pcb)
            if not result["success"]:
                self.wa.send_msg(ph, "🔄 محاول�� أخرى..."); result = self.dl.download_ytdlp(dl_url, fname, q)
            if not result["success"]:
                self.db.update_download(dl_id, status="failed", error_msg=result.get("error",""))
                self.wa.send_msg(ph, f"❌ فشل!\n{result.get('error','')}\nجرب سيرفر/موقع آخر"); return
            fp = result["filepath"]; sz = result["size_mb"]
            self.db.update_download(dl_id, status="downloaded", file_size_mb=round(sz,2))
            self.wa.send_msg(ph, f"✅ ({sz:.1f}MB)\n🔄 تجهيز...")
            comp = self.comp.compress_for_wa(fp)
            if not comp["success"]: self.wa.send_msg(ph, f"❌ ضغط: {comp.get('error','')}"); self._clean(fp); return
            if comp.get("split"):
                parts = comp["parts"]; self.wa.send_msg(ph, f"📦 {len(parts)} أجزاء")
                for p in parts:
                    self.wa.send_file(ph, p["path"], f"🎬 {title} S{sn}E{int(en)} جزء {p['part']}/{len(parts)}")
                    time.sleep(3)
            else:
                sp = comp["output"]; fm = comp.get("output_mb", 0)
                self.wa.send_msg(ph, "📤 إرسال...")
                if self.wa.send_file(ph, sp, f"🎬 *{title}*\n📺 S{sn}E{int(en)} | {q} | {fm:.1f}MB"):
                    self.db.update_download(dl_id, status="completed", compressed_size_mb=round(fm,2),
                        completed_at=datetime.now().isoformat(), sent_at=datetime.now().isoformat())
                    self.db.update_user(ph, total_downloads=user["total_downloads"]+1)
                    self.wa.send_msg(ph, "✅ *تم!*\n🔍 أرسل اسم أنمي آخر")
                else: self.wa.send_msg(ph, "❌ فشل الإرسال")
            self._clean(fp, comp)
        except Exception as e:
            print(f"❌ {e}"); import traceback; traceback.print_exc()
            self.wa.send_msg(ph, f"❌ {e}")

    def _clean(self, fp, comp=None):
        try:
            if os.path.exists(fp): os.remove(fp)
            if comp:
                if comp.get("split"):
                    for p in comp.get("parts",[]): 
                        if os.path.exists(p.get("path","")): os.remove(p["path"])
                elif comp.get("compressed"):
                    o = comp.get("output","")
                    if o and os.path.exists(o): os.remove(o)
        except: pass

if __name__ == "__main__":
    bot = AnimeBot()
    try: bot.start()
    except KeyboardInterrupt: print("\n👋"); bot.wa.close()
    except Exception as e: print(f"❌ {e}"); bot.wa.close()