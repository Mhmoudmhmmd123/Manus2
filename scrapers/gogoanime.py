import re
from .base_scraper import BaseScraper

class GogoAnimeScraper(BaseScraper):
    def search(self, query):
        results = []
        r = self.get(f"{self.base_url}/search.html?keyword={query}")
        if not r: return results
        s = self.soup(r.text)
        for item in (s.select(".items li") or s.select(".last_episodes li"))[:20]:
            a = item.select_one("a")
            if not a: continue
            href = a.get("href", "")
            if not href.startswith("http"): href = self.base_url + href
            title = a.get("title", "") or a.get_text(strip=True)
            img_el = item.select_one("img"); img = (img_el.get("src") or "") if img_el else ""
            results.append({"title_ar": title, "title_en": title, "url": href, "cover": img, "site": self.name})
        return results

    def get_seasons(self, url): return [{"num": 1, "title": "Season 1", "url": url}]

    def get_episodes(self, url):
        r = self.get(url)
        if not r: return []
        s = self.soup(r.text); eps = []
        ep_pages = s.select("#episode_page a")
        if ep_pages:
            alias = url.rstrip("/").split("/")[-1]
            for a in ep_pages:
                try:
                    start = int(a.get("ep_start", "0")); end = int(a.get("ep_end", "0"))
                    for n in range(max(start, 1), end + 1):
                        eps.append({"num": float(n), "title": f"Episode {n}", "url": f"{self.base_url}/{alias}-episode-{n}"})
                except: pass
        eps.sort(key=lambda x: x["num"]); return eps

    def get_download_links(self, url):
        r = self.get(url)
        if not r: return {}
        s = self.soup(r.text); links = {}
        for a in (s.select(".anime_muti_link a") or s.select("a[data-video]")):
            href = a.get("data-video") or a.get("href", "")
            if href.startswith("//"): href = "https:" + href
            if not href: continue
            sv = self.detect_server(href)
            if "720p" not in links: links["720p"] = {}
            links["720p"][sv] = href
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