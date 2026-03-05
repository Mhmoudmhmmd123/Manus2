import os, re, time, requests
from config import Config

class VideoDownloader:
    def __init__(self):
        self.s = requests.Session()
        self.s.headers.update({"User-Agent": "Mozilla/5.0 Chrome/120.0", "Accept": "*/*"})

    def download(self, url, filename=None, pcb=None):
        if not filename:
            filename = url.split("/")[-1].split("?")[0]
            if not filename.endswith((".mp4",".mkv")): filename += ".mp4"
        filename = re.sub(r"[^\w\-_.]", "_", filename)
        fp = os.path.join(Config.DOWNLOAD_DIR, filename)
        try:
            st = time.time()
            r = self.s.get(url, stream=True, timeout=Config.DOWNLOAD_TIMEOUT, allow_redirects=True)
            r.raise_for_status(); total = int(r.headers.get("content-length", 0)); dl = 0; lp = 0
            with open(fp, "wb") as f:
                for chunk in r.iter_content(chunk_size=Config.CHUNK_SIZE):
                    if chunk: f.write(chunk); dl += len(chunk)
                    if pcb and total:
                        pct = (dl/total)*100
                        if pct - lp >= 20: lp = pct; pcb(pct, dl/max(time.time()-st,0.1), dl, total)
            mb = os.path.getsize(fp)/(1024*1024)
            return {"success": True, "filepath": fp, "filename": filename, "size_mb": mb}
        except Exception as e:
            if os.path.exists(fp): os.remove(fp)
            return {"success": False, "error": str(e)}

    def download_ytdlp(self, url, filename=None, quality="720p"):
        try: import yt_dlp
        except: return {"success": False, "error": "no yt-dlp"}
        if not filename: filename = f"anime_{int(time.time())}.mp4"
        filename = re.sub(r"[^\w\-_.]", "_", filename)
        fp = os.path.join(Config.DOWNLOAD_DIR, filename)
        qm = {"240p":"240","360p":"360","480p":"480","720p":"720","1080p":"1080"}
        try:
            with yt_dlp.YoutubeDL({"outtmpl": fp, "format": f"best[height<={qm.get(quality,'720')}]/best", "merge_output_format": "mp4", "quiet": True}) as ydl:
                ydl.download([url])
            return {"success": True, "filepath": fp, "filename": filename, "size_mb": os.path.getsize(fp)/(1024*1024)}
        except Exception as e:
            if os.path.exists(fp): os.remove(fp)
            return {"success": False, "error": str(e)}