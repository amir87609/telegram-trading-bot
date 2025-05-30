import logging
import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MAX_SIGNALS_PER_DAY = 10

user_data = {}

signals = ["Buy", "Sell", "No clear signal"]

def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("Start Trading", callback_data="start_trading")],
        [InlineKeyboardButton("Market Status", callback_data="market_status")],
        [InlineKeyboardButton("Help", callback_data="help")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_amount_menu():
    keyboard = [
        [InlineKeyboardButton("$5", callback_data="amount_5")],
        [InlineKeyboardButton("$10", callback_data="amount_10")],
        [InlineKeyboardButton("$25", callback_data="amount_25")],
        [InlineKeyboardButton("$40", callback_data="amount_40")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_result_buttons():
    keyboard = [
        [
            InlineKeyboardButton("✅ I won", callback_data="win"),
            InlineKeyboardButton("❌ I lost", callback_data="lose")
        ],
        [
            InlineKeyboardButton("Main Menu", callback_data="main_menu")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_data:
        user_data[user_id] = {"signals_today": 0, "wins": 0, "losses": 0}
    await update.message.reply_text(
        "Welcome to the bot 🔥🫡",
        reply_markup=get_main_menu()
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "To start, click on 'Start Trading'.\n"
        "Choose an amount, then get your signal!\n"
        "Track your wins and losses easily."
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    # التأكد من تهيئة بيانات المستخدم
    if user_id not in user_data:
        user_data[user_id] = {"signals_today": 0, "wins": 0, "losses": 0}

    if query.data == "start_trading":
        await query.edit_message_text("Choose your amount:", reply_markup=get_amount_menu())

    elif query.data.startswith("amount_"):
        if user_data[user_id]["signals_today"] >= MAX_SIGNALS_PER_DAY:
            await query.edit_message_text(
                "You've reached the maximum signals for today. Come back tomorrow. 🔻",
                reply_markup=get_main_menu()
            )
        else:
            signal = random.choice(signals)
            user_data[user_id]["signals_today"] += 1
            context.user_data["last_signal"] = signal
            await query.edit_message_text(
                f"Market Signal: {signal}",
                reply_markup=get_result_buttons()
            )

    elif query.data == "market_status":
        status = random.choice(["Good", "Volatile"])
        await query.edit_message_text(
            f"Market Status: {status}",
            reply_markup=get_main_menu()
        )

    elif query.data == "help":
        await query.edit_message_text(
            "To start, click on 'Start Trading'.\n"
            "Choose amount, get signal, then record your result.",
            reply_markup=get_main_menu()
        )

    elif query.data == "win":
        user_data[user_id]["wins"] += 1
        await query.edit_message_text(
            "Well done! ✅\nTotal Wins: {}\n\nChoose an option:".format(user_data[user_id]["wins"]),
            reply_markup=get_main_menu()
        )

    elif query.data == "lose":
        user_data[user_id]["losses"] += 1
        await query.edit_message_text(
            "Don't worry! ❌\nTotal Losses: {}\n\nChoose an option:".format(user_data[user_id]["losses"]),
            reply_markup=get_main_menu()
        )

    elif query.data == "main_menu":
        await query.edit_message_text(
            "Main Menu:",
            reply_markup=get_main_menu()
        )

def main():
    TOKEN = os.getenv(" 8105076316:AAEjX4ds7PIugr_N-zarYZILHGqD2zFM-OY ")
    if not TOKEN:
        print("Error: BOT_TOKEN environment variable not set!")
        return

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
