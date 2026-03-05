from config import Config

class ScraperManager:
    def __init__(self):
        self.scrapers = {}; self._init()

    def _init(self):
        from .anime4up import Anime4upScraper
        from .witanime import WitAnimeScraper
        from .gogoanime import GogoAnimeScraper
        from .generic_scraper import GenericScraper
        cm = {"anime4up": Anime4upScraper, "witanime": WitAnimeScraper,
              "gogoanime": GogoAnimeScraper, "generic": GenericScraper}
        for sid, sc in Config.SITES.items():
            cls = cm.get(sc.get("scraper", "generic"), GenericScraper)
            try: self.scrapers[sid] = cls(sc)
            except: pass
        print(f"  ✅ {len(self.scrapers)} scrapers loaded")

    def get(self, sid): return self.scrapers.get(sid)

    def search(self, query, sid=None):
        results = []
        if sid and sid in self.scrapers:
            try: results = self.scrapers[sid].search(query)
            except Exception as e: print(f"  search err: {e}")
        else:
            for s, sc in list(self.scrapers.items())[:3]:
                try: results.extend(sc.search(query))
                except: continue
        return results

    def sites_text(self):
        t = "🌐 *المواقع:*\n\n📺 *عربية:*\n"
        for i, s in Config.SITES.items():
            if s["lang"] == "ar":
                st = "✅" if i in self.scrapers else "⚪"
                t += f"  {st} *{i}.* {s['name']}\n"
        t += "\n🌍 *إنجليزية:*\n"
        for i, s in Config.SITES.items():
            if s["lang"] == "en":
                st = "✅" if i in self.scrapers else "⚪"
                t += f"  {st} *{i}.* {s['name']}\n"
        return t