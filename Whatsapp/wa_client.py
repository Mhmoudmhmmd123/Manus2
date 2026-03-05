import json
import os, re, time, json
from config import Config

class WhatsAppClient:
    def __init__(self, db): self.db = db; self.driver = None; self.wait = None; self.connected = False

    def init_browser(self):
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.support.ui import WebDriverWait
        opts = Options()
        opts.add_argument("--no-sandbox")
        opts.add_argument("--headless")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--disable-dev-shm-usage")
        import random
        port = random.randint(10000, 60000)
        opts.add_argument(f"--remote-debugging-port={port}")
        sess = os.path.join(Config.SESSION_DIR, "chrome_data"); os.makedirs(sess, exist_ok=True)
        opts.add_argument(f"--user-data-dir={sess}")
        # التحقق من مسارات البيئة (GitHub Actions)
        chrome_bin = os.environ.get("CHROME_BIN", "/usr/bin/chromium-browser")
        chrome_driver = os.environ.get("CHROME_DRIVER", "/usr/bin/chromedriver")
        
        if os.path.exists(chrome_bin):
            opts.binary_location = chrome_bin
        elif os.path.exists("/usr/bin/google-chrome"):
            opts.binary_location = "/usr/bin/google-chrome"
        elif os.path.exists("/data/data/com.termux"):
            cb = "/data/data/com.termux/files/usr/bin/chromium-browser"
            if os.path.exists(cb): opts.binary_location = cb
            opts.add_argument("--headless"); opts.add_argument("--single-process")
            opts.add_argument("--no-zygote")

        try:
            from selenium.webdriver.chrome.service import Service
            driver_path = chrome_driver if os.path.exists(chrome_driver) else "/usr/bin/chromedriver"
            self.driver = webdriver.Chrome(service=Service(driver_path), options=opts)
        except Exception as e:
            print(f"  ❌ driver err: {e}")
            self.driver = webdriver.Chrome(options=opts)
        self.wait = WebDriverWait(self.driver, 90)
        print("  🌐 opening WhatsApp Web..."); self.driver.get("https://web.whatsapp.com")
        try:
            c = self.db._c(); x = c.cursor()
            x.execute("SELECT session_data FROM wa_sessions WHERE session_id='main' AND is_active=1")
            r = x.fetchone(); c.close()
            if r and r['session_data']:
                print("  🍪 Loading session from database...")
                cookies = json.loads(r['session_data'])
                for cookie in cookies:
                    try: self.driver.add_cookie(cookie)
                    except: pass
                self.driver.refresh(); time.sleep(5)
        except Exception as e: print(f"  ❌ session load err: {e}")

    def wait_login(self):
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        print("\n" + "="*50); print("  📱 Scan QR Code from WhatsApp"); print("="*50)
        try:
            # Wait for QR code or login
            qr_path = os.path.join(Config.BASE_DIR, "qr.png")
            print("  ⏳ Waiting for QR code to appear...")
            for i in range(60):
                try:
                    self.driver.save_screenshot(qr_path)
                    print(f"  📸 Screenshot saved to {qr_path} (attempt {i+1})")
                    try:
                        qr_canvas = self.driver.find_element(By.CSS_SELECTOR, 'canvas[aria-label="Scan this QR code to link a device"]')
                        qr_canvas.screenshot(qr_path)
                        print(f"  📸 QR Code cropped and saved to {qr_path}")
                    except: pass
                    break
                except Exception as e:
                    try:
                        self.driver.find_element(By.CSS_SELECTOR, "#pane-side, [data-testid='chat-list']")
                        print("  ✅ Already logged in!")
                        break
                    except: pass
                if i % 5 == 0: print(f"  ... still waiting ({i+1}/60)")
                time.sleep(2)

            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#pane-side, [data-testid='chat-list']")))
            self.connected = True; print("  ✅ Logged in!")
            try: self.db.save_session("main", json.dumps(self.driver.get_cookies()))
            except: pass
            return True
        except Exception as e: print(f"  ❌ {e}"); return False

    def send_msg(self, phone, text):
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.keys import Keys
        from selenium.webdriver.support import expected_conditions as EC
        try:
            phone = re.sub(r"[^0-9]", "", phone)
            self.driver.get(f"https://web.whatsapp.com/send?phone={phone}"); time.sleep(5)
            box = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,
                '[data-testid="conversation-compose-box-input"], div[contenteditable="true"][data-tab="10"], footer div[contenteditable="true"]')))
            for line in text.split("\n"): box.send_keys(line); box.send_keys(Keys.SHIFT + Keys.ENTER)
            box.send_keys(Keys.ENTER); time.sleep(2); return True
        except Exception as e: print(f"  msg err: {e}"); return False

    def send_file(self, phone, filepath, caption=""):
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.keys import Keys
        from selenium.webdriver.support import expected_conditions as EC
        try:
            phone = re.sub(r"[^0-9]", "", phone)
            self.driver.get(f"https://web.whatsapp.com/send?phone={phone}"); time.sleep(5)
            attach = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                '[data-testid="clip"], span[data-icon="clip"], span[data-icon="plus"]')))
            attach.click(); time.sleep(2)
            fi = self.driver.find_element(By.CSS_SELECTOR, 'input[type="file"]')
            fi.send_keys(os.path.abspath(filepath)); time.sleep(5)
            if caption:
                try:
                    cb = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,
                        '[data-testid="media-caption-input-container"] div[contenteditable]')))
                    cb.click()
                    for line in caption.split("\n"): cb.send_keys(line); cb.send_keys(Keys.SHIFT + Keys.ENTER)
                except: pass
            time.sleep(1)
            send = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="send"], span[data-icon="send"]')))
            send.click()
            mb = os.path.getsize(filepath)/(1024*1024); time.sleep(max(15, int(mb*3))); return True
        except Exception as e: print(f"  file err: {e}"); return False

    def listen(self, callback):
        from selenium.webdriver.common.by import By
        print("  👂 listening..."); seen = set()
        while self.connected:
            try:
                badges = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="icon-unread-count"], span[aria-label*="unread"]')
                for badge in badges:
                    try:
                        chat = badge.find_element(By.XPATH, './ancestor::div[@data-testid="cell-frame-container" or @role="listitem"]')
                        chat.click(); time.sleep(2)
                        msgs = self.driver.find_elements(By.CSS_SELECTOR, "div.message-in .copyable-text[data-pre-plain-text], div.message-in .selectable-text span")
                        if msgs:
                            text = msgs[-1].text.strip(); phone = self._phone(); mid = f"{phone}:{text}"
                            if mid not in seen and text:
                                seen.add(mid)
                                if len(seen) > 2000: seen = set(list(seen)[-1000:])
                                callback({"phone": phone, "text": text})
                    except: continue
                time.sleep(2)
            except: time.sleep(5)

    def _phone(self):
        from selenium.webdriver.common.by import By
        try:
            for sel in ['[data-testid="conversation-header"] span[title]', "header span[title]"]:
                els = self.driver.find_elements(By.CSS_SELECTOR, sel)
                if els:
                    t = els[0].get_attribute("title")
                    if t: return re.sub(r"[^0-9]", "", t)
        except: pass
        return "unknown"

    def close(self):
        if self.driver:
            try: self.driver.quit()
            except: pass