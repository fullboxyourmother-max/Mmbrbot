import asyncio
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
from bot import bot

# ---------------------------------------------------------
# وب‌سرور داخلی برای زنده نگه داشتن ربات روی Railway
# ---------------------------------------------------------
class RailwayHealthCheck(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Bale Bot is active and running!")
    def log_message(self, format, *args):
        return  

def start_health_server():
    port = int(os.getenv("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), RailwayHealthCheck)
    print(f"[Railway] Web server started on port {port}")
    server.serve_forever()

# ---------------------------------------------------------
# مدیریت پیام‌های ربات هویج (متنی و ۱۰۰٪ ایمن)
# ---------------------------------------------------------
@bot.event
async def on_ready():
    print(f"[Bot] @{bot.username} is online now!")

@bot.event
async def on_message(message):
    text = message.content

    if text == "/start":
        help_text = (
            "سلام فرمانده! به ربات هویج خوش آمدید. 🥕\n\n"
            "دستورات ربات:\n"
            "🔸 برای دیدن منو بنویسید: منو\n"
            "🔸 برای دیدن آمار بنویسید: آمار\n"
            "🔸 برای پشتیبانی بنویسید: پشتیبانی"
        )
        await message.reply(help_text)
    
    elif text == "منو":
        await message.reply("🎯 شما بخش منوی اصلی را انتخاب کردید.")
        
    elif text == "آمار":
        await message.reply(f"📊 آمار شما در حال حاضر خالی است.\nآیدی عددی شما: {message.author.id}")
        
    elif text == "پشتیبانی":
        await message.reply("📞 برای ارتباط با پشتیبانی پیام خود را بفرستید.")

# ---------------------------------------------------------
# تابع اصلی برای شروع به کار ربات
# ---------------------------------------------------------
async def main():
    print("[Bot] Connecting to @Havijbkbot ...")
    try:
        # تغییر مهم: استفاده از run به جای start
        bot.run()
    except Exception as e:
        print(f"[Error] Failed to start the bot: {e}")

if __name__ == "__main__":
    web_thread = threading.Thread(target=start_health_server, daemon=True)
    web_thread.start()
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("[Bot] Process stopped.")
