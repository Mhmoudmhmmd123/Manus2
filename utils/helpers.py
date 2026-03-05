import os, re, time

def clean_filename(n):
    n = re.sub(r"[^\w\s\-.]", "", n); return re.sub(r"\s+", "_", n)[:100]

def format_size(b):
    if b < 1024: return f"{b}B"
    if b < 1024**2: return f"{b/1024:.1f}KB"
    if b < 1024**3: return f"{b/1024**2:.1f}MB"
    return f"{b/1024**3:.2f}GB"

def format_time(s):
    if s < 60: return f"{s:.0f}s"
    return f"{s//60:.0f}m {s%60:.0f}s"

def cleanup_old(d, hours=6):
    if not os.path.exists(d): return
    now = time.time()
    for f in os.listdir(d):
        fp = os.path.join(d, f)
        if os.path.isfile(fp) and (now - os.path.getmtime(fp))/3600 > hours:
            try: os.remove(fp)
            except: pass