import os
import threading
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import bale
from bot import bot

# ---------------------------------------------------------
# تنظیمات اصلی ادمین (آیدی عددی شما)
# ---------------------------------------------------------
ADMIN_ID = "692466131"

# ---------------------------------------------------------
# پایگاه داده ساده متنی برای ذخیره اطلاعات کاربران
# ---------------------------------------------------------
DB_FILE = "users_db.json"

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ---------------------------------------------------------
# وب‌سرور داخلی برای زنده نگه داشتن ربات روی Railway
# ---------------------------------------------------------
class RailwayHealthCheck(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Bale Income Bot is Active!")
    def log_message(self, format, *args):
        return  

def start_health_server():
    port = int(os.getenv("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), RailwayHealthCheck)
    server.serve_forever()

# ---------------------------------------------------------
# کیبوردهای ربات با متد استاندارد کلاس Menu در پکیج بله
# ---------------------------------------------------------
def get_main_keyboard():
    return bale.Menu(
        [
            [bale.MenuButton("💎 شروع کسب درآمد 💎")],
            [bale.MenuButton("🏠 حساب کاربری"), bale.MenuButton("🌟 برترین کاربران")],
            [bale.MenuButton("💸 برداشت از حساب"), bale.MenuButton("📊 تاریخچه برداشت")],
            [bale.MenuButton("📜 قوانین"), bale.MenuButton("📞 پشتیبانی"), bale.MenuButton("📚 راهنما")]
        ]
    )

def get_admin_keyboard():
    return bale.Menu(
        [
            [bale.MenuButton("📊 آمار کل ربات"), bale.MenuButton("📢 ارسال پیام همگانی")],
            [bale.MenuButton("🔙 بازگشت به منو اصلی")]
        ]
    )

def get_withdraw_keyboard():
    return bale.Menu(
        [
            [bale.MenuButton("💳 کارت به کارت"), bale.MenuButton("🎁 پاکت هدیه")],
            [bale.MenuButton("🔙 بازگشت به منو اصلی")]
        ]
    )

def get_admin_option_keyboard():
    return bale.Menu(
        [
            [bale.MenuButton("🛠️ پنل ادمین")],
            [bale.MenuButton("🔙 بازگشت به منو اصلی")]
        ]
    )

# ---------------------------------------------------------
# مدیریت رویدادها و پیام‌های ربات
# ---------------------------------------------------------
@bot.event
async def on_ready():
    print("====================================")
    print(f"[Success] Bot @{bot.username} is fully ONLINE!")
    print("====================================")

@bot.event
async def on_message(message):
    user_id = str(message.author.id)
    text = message.content
    db = load_db()

    # ۱. ثبت نام کاربر جدید
    if user_id not in db:
        db[user_id] = {
            "balance": 0,
            "invited_by": None,
            "invites_count": 0,
            "username": message.author.username or "کاربر بله",
            "step": "none"
        }
        save_db(db)

    user_data = db[user_id]

    # ۲. بخش پاسخ‌های در انتظار (وضعیت‌ها یا Steps)
    if user_id == ADMIN_ID and user_data.get("step") == "broadcasting":
        db[ADMIN_ID]["step"] = "none"
        save_db(db)
        await message.reply("⏳ در حال ارسال پیام همگانی به تمام کاربران...")
        
        success_count = 0
        for uid in list(db.keys()):
            if uid == ADMIN_ID:
                continue
            try:
                await bot.send_message(int(uid), text)
                success_count += 1
            except:
                pass
        
        await message.reply(f"📢 پیام همگانی شما با موفقیت به {success_count} کاربر ارسال شد.", reply_markup=get_main_keyboard())
        return

    if user_data.get("step") == "entering_withdraw_amount":
        db[user_id]["step"] = "none"
        save_db(db)
        
        notification_text = (
            f"🚨 **درخواست جدید برداشت از حساب!**\n\n"
            f"👤 کاربر: {user_data['username']}\n"
            f"🆔 آیدی عددی: `{user_id}`\n"
            f"💰 مبلغ درخواستی: {text} تومان\n"
            f"💼 کل موجودی کاربر: {user_data['balance']:,} تومان"
        )
        try:
            await bot.send_message(int(ADMIN_ID), notification_text)
        except:
            pass
            
        await message.reply("✅ درخواست برداشت شما ثبت شد و برای ادمین ارسال گردید.", reply_markup=get_main_keyboard())
        return

    # ۳. دستورات متنی منو
    if text.startswith("/start"):
        parts = text.split()
        if len(parts) > 1:
            inviter_id = parts[1]
            if inviter_id in db and inviter_id != user_id and db[user_id]["invited_by"] is None:
                db[user_id]["invited_by"] = inviter_id
                db[inviter_id]["balance"] += 120000
                db[inviter_id]["invites_count"] += 1
                save_db(db)
                try:
                    await bot.send_message(
                        int(inviter_id), 
                        f"🎉 یک کاربر جدید با لینک شما وارد شد!\n💰 مبلغ ۱۲۰,۰۰۰ تومان به حساب شما اضافه شد."
                    )
                except:
                    pass

        welcome_text = "به ربات بمب خوش آمدید 🌹\nهر دعوت ≈ ۱۲۰,۰۰۰ تومان 💰\nموفق باشید☘️"
        await message.reply(welcome_text, reply_markup=get_main_keyboard())

    elif text == "💎 شروع کسب درآمد 💎":
        bot_text = (
            f"👇 با هر دعوت ۱۲۰,۰۰۰ تومان میده 👇\n"
            f"https://ble.ir/{bot.username}?start={user_id}\n"
            f"ربات رو استارت کن و پول به جیب بزن! 💸☝️\n\n"
            f"☝️ لینک اختصاصی شما ☝️\n"
            f"با پخش بنر بالا و هر دعوت ۱۲۰,۰۰۰ کسب کنید 🎁🥰"
        )
        await message.reply(bot_text)

    elif text == "🏠 حساب کاربری":
        profile_text = (
            f"👇 جزئیات حساب کاربری ({user_id}) 👇\n\n"
            f"💼 موجودی کیف پول شما: {user_data['balance']:,} تومان\n"
            f"👥 تعداد زیرمجموعه‌های شما: {user_data['invites_count']}\n"
            f"✅ تعداد زیرمجموعه‌های احراز شده: {user_data['invites_count']}\n"
            f"❌ تعداد زیرمجموعه‌های احراز نشده: 0"
        )
        if user_id == ADMIN_ID:
            await message.reply(profile_text + "\n\n⚙️ شما ادمین اصلی ربات هستید.", reply_markup=get_admin_option_keyboard())
        else:
            await message.reply(profile_text)

    elif text == "🌟 برترین کاربران":
        top_users = sorted(db.items(), key=lambda x: x[1]["invites_count"], reverse=True)[:5]
        leaderboard = "🌟 برترین کاربران 🌟\n\n"
        medals = ["🥇", "🥈", "🥉", "🏅", "🏅"]
        for i, (uid, udata) in enumerate(top_users):
            leaderboard += f"{medals[i]} - {udata['invites_count']} زیرمجموعه | {uid}\n"
        await message.reply(leaderboard)

    elif text == "💸 برداشت از حساب":
        await message.reply("لطفاً یکی از روش‌های برداشت زیر را انتخاب کنید:", reply_markup=get_withdraw_keyboard())

    elif text in ["💳 کارت به کارت", "🎁 پاکت هدیه"]:
        db[user_id]["step"] = "entering_withdraw_amount"
        save_db(db)
        await message.reply(f"💸 لطفاً مبلغ مورد نظر برای برداشت را وارد کنید:\n\n💰 موجودی حساب شما: {user_data['balance']:,} تومان")

    elif text == "📊 تاریخچه برداشت":
        await message.reply("📊 تاریخچه برداشت‌ها\n\n❌ هیچ برداشتی اخیر یافت نشد.")

    elif text == "📜 قوانین":
        await message.reply("📋 واریزی -\nصبور باشید بعد از برداشت شما پس از تایید داخل صف قرار می‌گیره.\nتا یک هفته پردازش انجام میشه و پرداخت میشه.")

    elif text == "📞 پشتیبانی":
        await message.reply("اگر سوالی دارید، تیم پشتیبانی بمب آماده پاسخگویی به شماست\n💬 پشتیبانی ۲۴ ساعته بمب:\nپیام خود را بگذارید")

    elif text == "📚 راهنما":
        help_guide = (
            "مرحله اول: ربات رو استارت کن\n"
            "مرحله دوم: بزن رو دکمه 💎 شروع کسب درآمد 💎\n"
            "مرحله سوم: لینک مخصوص رو برای همه دوستانت بفرست\n"
            "مرحله چهارم: بگو استارت کنن عضو کانال های بات بشن\n"
            "و در آخر با هر دعوت ۱۱۵,۰۰۰ تومان پاداش میگیری ❤️"
        )
        await message.reply(help_guide)

    elif text == "🔙 بازگشت به منو اصلی":
        db[user_id]["step"] = "none"
        save_db(db)
        await message.reply("به منوی اصلی بازگشتید.", reply_markup=get_main_keyboard())

    # دستورات ادمین
    elif text == "🛠️ پنل ادمین" and user_id == ADMIN_ID:
        await message.reply("به پنل مدیریت ربات هویج خوش آمدید، ادمین عزیز. 🥕", reply_markup=get_admin_keyboard())

    elif text == "📊 آمار کل ربات" and user_id == ADMIN_ID:
        total_users = len(db)
        await message.reply(f"📊 آمار کل ربات شما:\n\n👥 تعداد کل کاربران ثبت‌نام شده: {total_users} نفر")

    elif text == "📢 ارسال پیام همگانی" and user_id == ADMIN_ID:
        db[ADMIN_ID]["step"] = "broadcasting"
        save_db(db)
        await message.reply("✍️ لطفاً پیام خود را بفرستید تا برای تمام کاربران ربات ارسال شود:")

# ---------------------------------------------------------
# اجرای پروژه
# ---------------------------------------------------------
if __name__ == "__main__":
    web_thread = threading.Thread(target=start_health_server, daemon=True)
    web_thread.start()
    bot.run()
