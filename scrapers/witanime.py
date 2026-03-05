import re
from .base_scraper import BaseScraper

class WitAnimeScraper(BaseScraper):
    def search(self, query):
        results = []
        for path in [f"/?search_param=animes&s={query}", f"/?s={query}"]:
            r = self.get(self.base_url + path)
            if not r: continue
            s = self.soup(r.text)
            for a in (s.select(".anime-card-container a") or s.select("article a") or s.select("a[href]"))[:20]:
                href = a.get("href", "")
                if not href or href == "#": continue
                if not href.startswith("http"): href = self.base_url + href
                title = ""
                for sel in ["h3", ".anime-card-title", "img[alt]"]:
                    el = a.select_one(sel)
                    if el: title = el.get("alt", "") or el.get_text(strip=True); break
                if not title: title = a.get_text(strip=True)[:80]
                if title and len(title) > 2:
                    results.append({"title_ar": title, "url": href, "site": self.name})
            if results: break
        return results

    def get_seasons(self, url): return [{"num": 1, "title": "الموسم 1", "url": url}]

    def get_episodes(self, url):
        r = self.get(url)
        if not r: return []
        s = self.soup(r.text); eps = []
        for a in (s.select(".episodes-list a") or s.select("a[href*=episode]")):
            href = a.get("href", "")
            if not href: continue
            if not href.startswith("http"): href = self.base_url + href
            text = a.get_text(strip=True); num = re.search(r"(\d+)", text)
            eps.append({"num": float(num.group(1)) if num else 0, "title": text, "url": href})
        eps.sort(key=lambda x: x["num"]); return eps

    def get_download_links(self, url):
        r = self.get(url)
        if not r: return {}
        s = self.soup(r.text); links = {}
        for a in s.select("a[href]"):
            href = a.get("href", ""); text = a.get_text(strip=True).lower()
            if any(k in text for k in ["download","تحميل","server","سيرفر"]):
                q = "720p"
                for quality in ["240p","360p","480p","720p","1080p"]:
                    if quality in text: q = quality; break
                sv = self.detect_server(href)
                if q not in links: links[q] = {}
                links[q][sv] = href
        for iframe in s.find_all("iframe", src=True):
            src = iframe["src"]
            if src.startswith("//"): src = "https:" + src
            sv = self.detect_server(src)
            if "720p" not in links: links["720p"] = {}
            links["720p"][sv] = src
        return links

    def get_direct_link(self, url, quality="720p"):
        r = self.get(url)
        if not r: return None
        urls = self.find_videos(r.text)
        mp4s = [u for u in urls if ".mp4" in u.lower()]
        return mp4s[0] if mp4s else (urls[0] if urls else None)