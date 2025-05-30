import logging
import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

TOKEN = "8080679821:AAGO2n1NbKPvQExjrjwKsW99SFhOjEEh-fA"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MAX_SIGNALS_PER_DAY = 10
user_data = {}

BITCOIN_IMG_PATH = "btc.png"  # تأكد أن صورة بيتكوين بهذا الاسم بجانب هذا الملف

def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("ابدأ التداول", callback_data="start_trading")],
        [InlineKeyboardButton("حالة السوق", callback_data="market_status")],
        [InlineKeyboardButton("مساعدة", callback_data="help")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_amount_menu():
    keyboard = [
        [InlineKeyboardButton("5 دولار", callback_data="amount_5")],
        [InlineKeyboardButton("10 دولار", callback_data="amount_10")],
        [InlineKeyboardButton("25 دولار", callback_data="amount_25")],
        [InlineKeyboardButton("40 دولار", callback_data="amount_40")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_result_buttons():
    keyboard = [
        [
            InlineKeyboardButton("✅ ربحت", callback_data="win"),
            InlineKeyboardButton("❌ خسرت", callback_data="lose")
        ],
        [
            InlineKeyboardButton("القائمة الرئيسية", callback_data="main_menu")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_data:
        user_data[user_id] = {"signals_today": 0, "wins": 0, "losses": 0}
    await update.message.reply_text(
        "مرحباً بك في بوت التداول العربي 🔥💹",
        reply_markup=get_main_menu()
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "لبدء التداول اضغط على 'ابدأ التداول'.\n"
        "اختر المبلغ المطلوب، وستصلك إشارة دخول مع صورة وتحليل حقيقي.\n"
        "بعد التداول علم إذا ربحت أو خسرت لتتبع نتائجك.\n"
        "بالتوفيق! 🚀"
    )

async def fetch_prices():
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    params = {"vs_currency": "usd", "days": "1", "interval": "hourly"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            data = await resp.json()
            prices = [p[1] for p in data["prices"]]
            return prices

def calc_rsi(prices, period=14):
    if len(prices) < period + 1:
        return None
    gains, losses = [], []
    for i in range(1, period + 1):
        diff = prices[-i] - prices[-i-1]
        if diff > 0:
            gains.append(diff)
        else:
            losses.append(abs(diff))
    avg_gain = sum(gains) / period if gains else 0
    avg_loss = sum(losses) / period if losses else 0
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return round(rsi, 2)

def signal_from_rsi(rsi):
    if rsi is None:
        return "لا توجد بيانات كافية للتحليل حالياً."
    if rsi < 30:
        return "اشترِ الآن (RSI منخفض جداً) 📈"
    elif rsi > 70:
        return "بيع الآن (RSI مرتفع جداً) 📉"
    else:
        return "انتظر، السوق غير واضح حالياً 🚦"

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if user_id not in user_data:
        user_data[user_id] = {"signals_today": 0, "wins": 0, "losses": 0}

    if query.data == "start_trading":
        await query.edit_message_text(
            "اختر المبلغ الذي تريد التداول به:",
            reply_markup=get_amount_menu()
        )

    elif query.data.startswith("amount_"):
        if user_data[user_id]["signals_today"] >= MAX_SIGNALS_PER_DAY:
            await query.edit_message_text(
                "وصلت للحد اليومي للإشارات. جرب غداً بإذن الله. 🔻",
                reply_markup=get_main_menu()
            )
        else:
            try:
                prices = await fetch_prices()
                rsi = calc_rsi(prices)
                signal_text = signal_from_rsi(rsi)
                user_data[user_id]["signals_today"] += 1
                context.user_data["last_signal"] = signal_text

                caption = (
                    f"إشارتك اليوم (تحليل حقيقي):\n\n"
                    f"{signal_text}\n\n"
                    f"مؤشر RSI الحالي: {rsi if rsi else '---'}"
                )
                with open(BITCOIN_IMG_PATH, "rb") as photo:
                    await context.bot.send_photo(
                        chat_id=query.message.chat_id,
                        photo=photo,
                        caption=caption,
                        reply_markup=get_result_buttons()
                    )
                # لا داعي لحذف الرسالة القديمة، الأزرار ستبقى تعمل بشكل ممتاز
            except Exception as e:
                await query.edit_message_text(
                    f"حصل خطأ أثناء جلب التحليل: {e}",
                    reply_markup=get_main_menu()
                )

    elif query.data == "market_status":
        prices = await fetch_prices()
        ma = round(sum(prices[-20:]) / 20, 2) if len(prices) >= 20 else "---"
        last_price = prices[-1] if prices else "---"
        await query.edit_message_text(
            f"آخر سعر للبيتكوين: {last_price}$\nالمتوسط المتحرك 20 ساعة: {ma}$",
            reply_markup=get_main_menu()
        )

    elif query.data == "help":
        await query.edit_message_text(
            "لبدء التداول اضغط على 'ابدأ التداول'.\n"
            "اختر المبلغ، ثم انتظر الإشارة مع صورة وتحليل حقيقي.\n"
            "بعد التداول علّم إذا ربحت أو خسرت.",
            reply_markup=get_main_menu()
        )

    elif query.data == "win":
        user_data[user_id]["wins"] += 1
        await query.edit_message_text(
            f"مبروك الربح! ✅\nعدد أرباحك: {user_data[user_id]['wins']}\n\nاختر من القائمة:",
            reply_markup=get_main_menu()
        )

    elif query.data == "lose":
        user_data[user_id]["losses"] += 1
        await query.edit_message_text(
            f"حظاً أوفر في الصفقة القادمة! ❌\nعدد خسائرك: {user_data[user_id]['losses']}\n\nاختر من القائمة:",
            reply_markup=get_main_menu()
        )

    elif query.data == "main_menu":
        await query.edit_message_text(
            "القائمة الرئيسية:",
            reply_markup=get_main_menu()
        )

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
