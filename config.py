import os

class Config:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, "db.sqlite3")
    DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")
    COMPRESSED_DIR = os.path.join(BASE_DIR, "compressed")
    TEMP_DIR = os.path.join(BASE_DIR, "temp")
    SESSION_DIR = os.path.join(BASE_DIR, "session")
    LOG_DIR = os.path.join(BASE_DIR, "logs")
    MAX_FILE_SIZE_MB = 95
    DOWNLOAD_TIMEOUT = 600
    CHUNK_SIZE = 1024 * 64
    FFMPEG_PATH = "ffmpeg"

    COMPRESSION_PRESETS = {
        "ultra_low": {"crf": 38, "preset": "ultrafast", "resolution": "426x240"},
        "low":       {"crf": 34, "preset": "veryfast",  "resolution": "640x360"},
        "medium":    {"crf": 30, "preset": "fast",      "resolution": "854x480"},
        "high":      {"crf": 26, "preset": "medium",    "resolution": "1280x720"},
        "ultra":     {"crf": 22, "preset": "slow",      "resolution": "1920x1080"},
    }

    QUALITIES = ["240p", "360p", "480p", "720p", "1080p"]

    SITES = {
        1:  {"name": "Anime4up",     "url": "https://anime4up.cam",      "lang": "ar", "scraper": "anime4up"},
        2:  {"name": "WitAnime",     "url": "https://witanime.cyou",     "lang": "ar", "scraper": "witanime"},
        3:  {"name": "AnimeLek",     "url": "https://animelek.me",       "lang": "ar", "scraper": "generic"},
        4:  {"name": "AnimeBlkom",   "url": "https://animeblkom.net",    "lang": "ar", "scraper": "generic"},
        5:  {"name": "AnimeRco",     "url": "https://animerco.org",      "lang": "ar", "scraper": "generic"},
        6:  {"name": "AnimeSanka",   "url": "https://animesanka.com",    "lang": "ar", "scraper": "generic"},
        7:  {"name": "OkAnime",      "url": "https://okanime.tv",        "lang": "ar", "scraper": "generic"},
        8:  {"name": "ShahiidAnime", "url": "https://shahiid-anime.net", "lang": "ar", "scraper": "generic"},
        9:  {"name": "AnimeCloud",   "url": "https://animecloud.tv",     "lang": "ar", "scraper": "generic"},
        10: {"name": "XSAnime",      "url": "https://xsanime.com",       "lang": "ar", "scraper": "generic"},
        11: {"name": "AnimeStars",   "url": "https://animestars.org",    "lang": "ar", "scraper": "generic"},
        12: {"name": "AnimeTak",     "url": "https://animetak.net",      "lang": "ar", "scraper": "generic"},
        13: {"name": "Arabsama",     "url": "https://arabsama.net",      "lang": "ar", "scraper": "generic"},
        14: {"name": "Egyanime",     "url": "https://egyanime.com",      "lang": "ar", "scraper": "generic"},
        15: {"name": "Animeiat",     "url": "https://animeiat.tv",       "lang": "ar", "scraper": "generic"},
        16: {"name": "JustAnime",    "url": "https://justanime.me",      "lang": "ar", "scraper": "generic"},
        17: {"name": "AnimeMaster",  "url": "https://animemaster.cc",    "lang": "ar", "scraper": "generic"},
        18: {"name": "AnimeDown",    "url": "https://animedown.tv",      "lang": "ar", "scraper": "generic"},
        19: {"name": "AnimeY",       "url": "https://animey.cc",         "lang": "ar", "scraper": "generic"},
        20: {"name": "AnimeKSA",     "url": "https://animeksa.tv",       "lang": "ar", "scraper": "generic"},
        21: {"name": "FasrHD",       "url": "https://fasrhd.com",        "lang": "ar", "scraper": "generic"},
        22: {"name": "AnimeFlvAR",   "url": "https://animeflv.ar",       "lang": "ar", "scraper": "generic"},
        23: {"name": "AnimeSail",    "url": "https://animesail.com",     "lang": "ar", "scraper": "generic"},
        24: {"name": "AnimeRush",    "url": "https://animerush.ar",      "lang": "ar", "scraper": "generic"},
        25: {"name": "TurkAnimeAR",  "url": "https://turkanime.ar",      "lang": "ar", "scraper": "generic"},
        26: {"name": "GogoAnime",    "url": "https://gogoanime3.co",     "lang": "en", "scraper": "gogoanime"},
        27: {"name": "9Anime",       "url": "https://9anime.to",         "lang": "en", "scraper": "generic"},
        28: {"name": "Zoro",         "url": "https://zoro.to",           "lang": "en", "scraper": "generic"},
        29: {"name": "AnimePahe",    "url": "https://animepahe.ru",      "lang": "en", "scraper": "generic"},
        30: {"name": "KissAnime",    "url": "https://kissanime.com.ru",  "lang": "en", "scraper": "generic"},
        31: {"name": "AnimeFreak",   "url": "https://animefreak.tv",     "lang": "en", "scraper": "generic"},
        32: {"name": "AnimeFlix",    "url": "https://animeflix.live",     "lang": "en", "scraper": "generic"},
        33: {"name": "AnimeOwl",     "url": "https://animeowl.us",       "lang": "en", "scraper": "generic"},
        34: {"name": "AnimeFox",     "url": "https://animefox.tv",       "lang": "en", "scraper": "generic"},
        35: {"name": "AniWatch",     "url": "https://aniwatch.to",       "lang": "en", "scraper": "generic"},
        36: {"name": "KickAssAnime", "url": "https://kickassanime.am",   "lang": "en", "scraper": "generic"},
        37: {"name": "AnimeDao",     "url": "https://animedao.to",       "lang": "en", "scraper": "generic"},
        38: {"name": "AnimeHeaven",  "url": "https://animeheaven.me",    "lang": "en", "scraper": "generic"},
        39: {"name": "AnimeSuge",    "url": "https://animesuge.to",      "lang": "en", "scraper": "generic"},
        40: {"name": "AnimixPlay",   "url": "https://animixplay.to",     "lang": "en", "scraper": "generic"},
        41: {"name": "Nyaa",         "url": "https://nyaa.si",           "lang": "en", "scraper": "generic"},
        42: {"name": "AnimeKisa",    "url": "https://animekisa.tv",      "lang": "en", "scraper": "generic"},
        43: {"name": "AnimeUltima",  "url": "https://animeultima.to",    "lang": "en", "scraper": "generic"},
        44: {"name": "DarkAnime",    "url": "https://darkanime.stream",  "lang": "en", "scraper": "generic"},
        45: {"name": "AnimeSimple",  "url": "https://animesimple.com",   "lang": "en", "scraper": "generic"},
        46: {"name": "AnimeBee",     "url": "https://animebee.to",       "lang": "en", "scraper": "generic"},
        47: {"name": "YugenAnime",   "url": "https://yugenanime.tv",     "lang": "en", "scraper": "generic"},
        48: {"name": "AllAnime",     "url": "https://allanime.to",       "lang": "en", "scraper": "generic"},
        49: {"name": "Crunchyroll",  "url": "https://crunchyroll.com",   "lang": "en", "scraper": "generic"},
        50: {"name": "WCOStream",    "url": "https://wcostream.tv",      "lang": "en", "scraper": "generic"},
    }

    SERVERS = [
        "mp4upload", "vidstream", "streamtape", "doodstream",
        "fembed", "mixdrop", "upstream", "vidoza",
        "streamsb", "vidmoly", "uqload", "voe",
        "filemoon", "vtube", "megaup", "gounlimited"
    ]

    @classmethod
    def setup_dirs(cls):
        for d in [cls.DOWNLOAD_DIR, cls.COMPRESSED_DIR, cls.TEMP_DIR, cls.SESSION_DIR, cls.LOG_DIR]:
            os.makedirs(d, exist_ok=True)

Config.setup_dirs()