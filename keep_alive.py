#!/usr/bin/env python3
"""
نظام الإبقاء على البوت نشطاً - Keep Alive System
"""

import threading
import time
import signal
import sys
import os
from datetime import datetime

class BotKeeper:
    """فصل متخصص للإبقاء على البوت نشطاً"""
    
    def __init__(self, bot):
        self.bot = bot
        self.running = True
        self.start_time = datetime.now()
        self.heartbeat_interval = 30  # ثانية
        self.setup_signal_handlers()
        print("  ✅ keeper")
    
    def setup_signal_handlers(self):
        """التعامل مع إشارات النظام للإيقاف النظيف"""
        signal.signal(signal.SIGINT, self.stop)
        signal.signal(signal.SIGTERM, self.stop)
    
    def stop(self, *args):
        """إيقاف البوت بشكل نظيف"""
        print("\n\n🛑 جاري إيقاف البوت بشكل نظيف...")
        self.running = False
        
        # إغلاق اتصال واتساب إذا كان موجوداً
        if hasattr(self.bot, 'wa') and self.bot.wa:
            try:
                self.bot.wa.close()
            except:
                pass
        
        print("✅ تم إيقاف البوت بنجاح")
        sys.exit(0)
    
    def heartbeat(self):
        """خيط منفصل لإظهار أن البوت لا يزال يعمل"""
        counter = 0
        while self.running:
            time.sleep(self.heartbeat_interval)
            counter += 1
            
            # كل دقيقة (30 * 2)
            if counter % 2 == 0:
                elapsed = datetime.now() - self.start_time
                minutes = int(elapsed.total_seconds() / 60)
                print(f"💓 البوت لا يزال يعمل... {minutes} دقيقة")
                
                # التحقق من اتصال واتساب
                if hasattr(self.bot, 'wa') and self.bot.wa:
                    try:
                        if hasattr(self.bot.wa, 'is_connected') and not self.bot.wa.is_connected():
                            print("⚠️ اتصال واتساب مفقود، محاولة إعادة الاتصال...")
                            if hasattr(self.bot.wa, 'reconnect'):
                                self.bot.wa.reconnect()
                    except:
                        pass
    
    def monitor_listener(self):
        """مراقبة خيط الاستماع"""
        check_interval = 10  # ثوان
        while self.running:
            time.sleep(check_interval)
            
            # التحقق من وجود خيط الاستماع
            listener_alive = False
            for thread in threading.enumerate():
                if thread.name == "WhatsAppListener":
                    listener_alive = thread.is_alive()
                    break
            
            if not listener_alive and self.running:
                print("⚠️ خيط الاستماع توقف، إعادة تشغيله...")
                listener_thread = threading.Thread(
                    target=self.bot.wa.listen, 
                    args=(self.bot.on_msg,), 
                    name="WhatsAppListener",
                    daemon=True
                )
                listener_thread.start()
                print("✅ تم إعادة تشغيل خيط الاستماع")
    
    def keep_alive(self):
        """إبقاء البوت نشطاً"""
        # تشغيل نبضات القلب
        heartbeat_thread = threading.Thread(target=self.heartbeat, daemon=True)
        heartbeat_thread.start()
        
        # تشغيل مراقب الخيط
        monitor_thread = threading.Thread(target=self.monitor_listener, daemon=True)
        monitor_thread.start()
        
        print("\n" + "="*50)
        print("  ✅ BOT IS RUNNING!")
        print(f"  ⏳ بدأ التشغيل: {self.start_time.strftime('%H:%M:%S')}")
        print("  📱 أرسل اسم أنمي على واتساب")
        print("  🛑 اضغط Ctrl+C للإيقاف")
        print("="*50 + "\n")
        
        # الحلقة الرئيسية - تبقي البرنامج شغالاً
        while self.running:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                self.stop()
            except Exception as e:
                print(f"❌ خطأ في الحلقة الرئيسية: {e}")
                time.sleep(5)
