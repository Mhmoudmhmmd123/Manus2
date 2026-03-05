import re
from .base_scraper import BaseScraper

class GenericScraper(BaseScraper):
    def search(self, query):
        results = []
        for path in [f"/?s={query}", f"/?search_param=animes&s={query}", f"/search?q={query}"]:
            r = self.get(self.base_url + path)
            if not r: continue
            s = self.soup(r.text)
            for a in s.select("a[href]")[:30]:
                href = a.get("href", ""); title = a.get("title", "") or a.get_text(strip=True)
                if not title or len(title) < 3: continue
                if not href.startswith("http"): href = self.base_url + href
                if any(k in href.lower() for k in ["anime","series","watch"]):
                    results.append({"title_ar": title[:100], "url": href, "site": self.name})
            if results: break
        seen = set(); uniq = []
        for r2 in results[:15]:
            if r2["url"] not in seen: seen.add(r2["url"]); uniq.append(r2)
        return uniq

    def get_seasons(self, url): return [{"num": 1, "title": "الموسم 1", "url": url}]

    def get_episodes(self, url):
        r = self.get(url)
        if not r: return []
        s = self.soup(r.text); eps = []
        for a in s.select("a[href]"):
            href = a.get("href", ""); text = a.get_text(strip=True)
            if any(k in href.lower() or k in text.lower() for k in ["episode","حلقة"]):
                if not href.startswith("http"): href = self.base_url + href
                num = re.search(r"(\d+)", text)
                eps.append({"num": float(num.group(1)) if num else 0, "title": text[:80], "url": href})
        seen = set(); uniq = []
        for e in eps:
            if e["url"] not in seen: seen.add(e["url"]); uniq.append(e)
        uniq.sort(key=lambda x: x["num"]); return uniq

    def get_download_links(self, url):
        r = self.get(url)
        if not r: return {}
        s = self.soup(r.text); links = {}
        for iframe in s.find_all("iframe", src=True):
            src = iframe["src"]
            if src.startswith("//"): src = "https:" + src
            sv = self.detect_server(src)
            if "720p" not in links: links["720p"] = {}
            links["720p"][sv] = src
        for a in s.select("a[href]"):
            text = a.get_text(strip=True).lower()
            if any(k in text for k in ["download","تحميل","server"]):
                href = a.get("href", "")
                if not href.startswith("http"): href = self.base_url + href
                sv = self.detect_server(href)
                if "720p" not in links: links["720p"] = {}
                links["720p"][sv] = href
        for script in s.find_all("script"):
            if script.string:
                for u in self.find_videos(script.string):
                    sv = self.detect_server(u)
                    if "720p" not in links: links["720p"] = {}
                    links["720p"][sv] = u
        return links

    def get_direct_link(self, url, quality="720p"):
        r = self.get(url)
        if not r: return None
        urls = self.find_videos(r.text)
        mp4s = [u for u in urls if ".mp4" in u.lower()]
        return mp4s[0] if mp4s else (urls[0] if urls else None)