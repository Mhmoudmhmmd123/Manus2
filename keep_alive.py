import threading
import time
import signal
import sys
import os

class BotKeeper:
    """فصل متخصص للإبقاء على البوت نشطاً"""
    
    def __init__(self, bot):
        self.bot = bot
        self.running = True
        self.setup_signal_handlers()
    
    def setup_signal_handlers(self):
        """التعامل مع إشارات النظام للإيقاف النظيف"""
        signal.signal(signal.SIGINT, self.stop)
        signal.signal(signal.SIGTERM, self.stop)
    
    def stop(self, *args):
        """إيقاف البوت بشكل نظيف"""
        print("\n🛑 جاري إيقاف البوت...")
        self.running = False
    
    def start_heartbeat(self):
        """خيط منفصل لإظهار أن البوت لا يزال يعمل"""
        def heartbeat():
            counter = 0
            while self.running:
                time.sleep(30)
                counter += 1
                if counter % 2 == 0:  # كل دقيقة
                    print(f"💓 البوت لا يزال يعمل... ({counter//2} دقيقة)")
        
        thread = threading.Thread(target=heartbeat, daemon=True)
        thread.start()
    
    def keep_alive(self):
        """إبقاء البوت نشطاً"""
        self.start_heartbeat()
        print("✅ نظام الإبقاء على البوت نشط")
        print("⏳ البوت يعمل... اضغط Ctrl+C للإيقاف")
        
        while self.running:
            try:
                # هنا يمكن إضافة أي فحوصات دورية
                time.sleep(1)
            except Exception as e:
                print(f"❌ خطأ في الحلقة الرئيسية: {e}")
                time.sleep(5)

# للاستخدام المباشر في السكربتات البسيطة
def simple_keep_alive():
    """نسخة مبسطة للإبقاء على البوت نشطاً"""
    print("✅ البوت يعمل...")
    try:
        while True:
            time.sleep(60)
            print("💓 نبض: البوت لا يزال يعمل")
    except KeyboardInterrupt:
        print("\n👋 تم إيقاف البوت")
