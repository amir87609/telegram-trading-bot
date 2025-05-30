from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

BOT_TOKEN = '8080679821:AAGO2n1NbKPvQExjrjwKsW99SFhOjEEh-fA'

user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data[update.effective_user.id] = {"balance": 0, "profit": 0, "loss": 0, "last_amount": 0}
    await update.message.reply_text(
        "Welcome to the Trading Bot!\n\nChoose your trade amount:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("5$", callback_data='amount_5')],
            [InlineKeyboardButton("10$", callback_data='amount_10')]
        ])
    )

async def set_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = user_data.setdefault(query.from_user.id, {"balance": 0, "profit": 0, "loss": 0, "last_amount": 0})

    if query.data == 'amount_5':
        user["last_amount"] = 5
    elif query.data == 'amount_10':
        user["last_amount"] = 10

    await query.edit_message_text(
        f"Trade amount selected: {user['last_amount']}$\n\nType 'analyze' to get a market analysis."
    )

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # وهمي: تحليل السوق دائماً "Market is stable"
    analysis = "📊 Fake Analysis: Market is stable."
    await update.message.reply_text(analysis + "\n\nAfter your trade, press the appropriate button:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Win ✅", callback_data='result_win')],
            [InlineKeyboardButton("Lose ❌", callback_data='result_lose')]
        ])
    )

async def trade_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = user_data.setdefault(query.from_user.id, {"balance": 0, "profit": 0, "loss": 0, "last_amount": 0})

    if query.data == 'result_win':
        user["profit"] += user["last_amount"]
        msg = f"You won this trade! 💰\nTotal profit: {user['profit']}$\nTotal loss: {user['loss']}$"
    elif query.data == 'result_lose':
        user["loss"] += user["last_amount"]
        msg = f"You lost this trade. 😢\nTotal profit: {user['profit']}$\nTotal loss: {user['loss']}$"
    else:
        msg = "Unknown option"

    await query.edit_message_text(msg)

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("^analyze$"), analyze))
    app.add_handler(CallbackQueryHandler(set_amount, pattern="^amount_"))
    app.add_handler(CallbackQueryHandler(trade_result, pattern="^result_"))
    app.run_polling()
