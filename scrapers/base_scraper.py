import re, time, random, requests
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod

try:
    import cloudscraper; HAS_CS = True
except: HAS_CS = False

try:
    from fake_useragent import UserAgent; UA = UserAgent()
except: UA = None

class BaseScraper(ABC):
    def __init__(self, sc):
        self.name = sc["name"]; self.base_url = sc["url"].rstrip("/"); self.lang = sc["lang"]
        ua = UA.random if UA else "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 Chrome/120.0 Mobile Safari/537.36"
        self.session = cloudscraper.create_scraper(browser={"browser":"chrome","platform":"linux","desktop":True}) if HAS_CS else requests.Session()
        self.session.headers.update({"User-Agent": ua, "Accept": "text/html,*/*", "Accept-Language": "ar,en;q=0.9", "Referer": self.base_url+"/"})

    def get(self, url, retries=3):
        for i in range(retries):
            try:
                r = self.session.get(url, timeout=30, allow_redirects=True)
                if r.status_code == 200: return r
                time.sleep(random.uniform(1,3))
            except Exception as e:
                if i == retries-1: print(f"  err {self.name}: {e}")
                time.sleep(2)
        return None

    def soup(self, html):
        try: return BeautifulSoup(html, "lxml")
        except: return BeautifulSoup(html, "html.parser")

    def find_videos(self, html):
        urls = set()
        try:
            s = self.soup(html)
            for iframe in s.find_all("iframe", src=True):
                src = iframe["src"]
                if src.startswith("//"): src = "https:" + src
                urls.add(src)
        except: pass
        for p in [r'https?://[^\s"<>]+\.mp4(?:\\?[^\s"<>]*)?'  , r'https?://[^\s"<>]+\.m3u8(?:\\?[^\s"<>]*)?'  ,
                  r'file\s*:\s*["\']([^"\']+)["\']' , r'source\s*:\s*["\']([^"\']+)["\']' ]:
            try:
                for m in re.finditer(p, html):
                    u = m.group(1) if m.lastindex else m.group()
                    if u.startswith("//"): u = "https:" + u
                    urls.add(u)
            except: pass
        return list(urls)

    def detect_server(self, url):
        ul = url.lower()
        for n, ps in {"mp4upload":["mp4upload"],"vidstream":["vidstream","gogoplay"],"streamtape":["streamtape"],
            "doodstream":["dood","d0000d"],"fembed":["fembed"],"mixdrop":["mixdrop"],"upstream":["upstream"],
            "vidoza":["vidoza"],"streamsb":["streamsb","sbembed"],"uqload":["uqload"],"voe":["voe.sx"],
            "filemoon":["filemoon"],"vtube":["vtube"]}.items():
            if any(p in ul for p in ps): return n
        return "other"

    @abstractmethod
    def search(self, q): pass
    @abstractmethod
    def get_seasons(self, url): pass
    @abstractmethod
    def get_episodes(self, url): pass
    @abstractmethod
    def get_download_links(self, url): pass
    @abstractmethod
    def get_direct_link(self, url, q="720p"): pass