import re
from .base_scraper import BaseScraper

class Anime4upScraper(BaseScraper):
    def search(self, query):
        results = []
        r = self.get(f"{self.base_url}/?search_param=animes&s={query}")
        if not r: return results
        s = self.soup(r.text)
        for card in (s.select(".anime-card-container a") or s.select("a[href*=anime]"))[:20]:
            try:
                href = card.get("href", "")
                if not href: continue
                if not href.startswith("http"): href = self.base_url + href
                title = ""
                for sel in [".anime-card-title", "h3", "img[alt]"]:
                    el = card.select_one(sel)
                    if el: title = el.get("alt", "") or el.get_text(strip=True); break
                if not title: title = card.get_text(strip=True)[:80]
                if not title: continue
                img_el = card.select_one("img")
                img = (img_el.get("src") or img_el.get("data-src", "")) if img_el else ""
                results.append({"title_ar": title, "url": href, "cover": img, "site": self.name})
            except: continue
        return results

    def get_seasons(self, url):
        r = self.get(url)
        if not r: return [{"num": 1, "title": "الموسم 1", "url": url}]
        s = self.soup(r.text)
        tabs = s.select(".seasons-tab a") or s.select(".season-link")
        if tabs:
            seasons = []
            for i, t in enumerate(tabs, 1):
                href = t.get("href", url)
                if not href.startswith("http"): href = self.base_url + href
                seasons.append({"num": i, "title": t.get_text(strip=True) or f"الموسم {i}", "url": href})
            return seasons
        return [{"num": 1, "title": "الموسم 1", "url": url}]

    def get_episodes(self, url):
        r = self.get(url)
        if not r: return []
        s = self.soup(r.text)
        eps = []
        for a in (s.select(".episodes-card-container a") or s.select("a[href*=episode]")):
            href = a.get("href", "")
            if not href: continue
            if not href.startswith("http"): href = self.base_url + href
            text = a.get_text(strip=True)
            num = re.search(r"(\d+)", text)
            eps.append({"num": float(num.group(1)) if num else 0, "title": text, "url": href})
        eps.sort(key=lambda x: x["num"]); return eps

    def get_download_links(self, url):
        r = self.get(url)
        if not r: return {}
        s = self.soup(r.text); links = {}
        for tab in s.select(".tab-content .tab-pane") or [s]:
            for a in tab.select("a[href]"):
                href = a.get("href", "")
                if not href.startswith("http"): continue
                text = a.get_text(strip=True); q = "720p"
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