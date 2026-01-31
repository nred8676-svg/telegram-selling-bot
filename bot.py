from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
USDT_ADDRESS = os.getenv("USDT_ADDRESS")

users = set()
orders = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users.add(update.effective_user.id)
    keyboard = [
        [InlineKeyboardButton("🔥 VIP – ₹149 / 2 USDT", callback_data="vip")],
        [InlineKeyboardButton("💎 Premium – ₹299 / 4 USDT", callback_data="premium")],
        [InlineKeyboardButton("👑 Lifetime – ₹999 / 12 USDT", callback_data="life")]
    ]
    await update.message.reply_text(
        "Welcome 👋\nChoose a plan:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def plan_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    orders[q.from_user.id] = q.data
    keyboard = [
        [InlineKeyboardButton("🌍 Pay via USDT (TRC20)", callback_data="usdt")],
        [InlineKeyboardButton("🎁 Pay via Gift Card", callback_data="gift")]
    ]
    await q.edit_message_text(
        "Choose payment method:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def payment_method(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data == "usdt":
        await q.edit_message_text(
            f"Send USDT (TRC20) to:\n{USDT_ADDRESS}\n\nAfter payment, send TxID here."
        )
    elif q.data == "gift":
        await q.edit_message_text(
            "Send Gift Card code here.\n\nSupported:\nAmazon / Flipkart / Google Play"
        )

async def messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid != ADMIN_ID:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"📩 From {uid}:\n{update.message.text}"
        )
        await update.message.reply_text("✅ Admin ko bhej diya gaya")
    else:
        if update.message.reply_to_message:
            try:
                to_uid = int(update.message.reply_to_message.text.split()[2])
                await context.bot.send_message(chat_id=to_uid, text=update.message.text)
            except:
                pass

async def panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_ID:
        await update.message.reply_text(
            f"📊 Admin Panel\nUsers: {len(users)}\nPending orders: {len(orders)}"
        )

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("panel", panel))
    app.add_handler(CallbackQueryHandler(plan_select, pattern="^(vip|premium|life)$"))
    app.add_handler(CallbackQueryHandler(payment_method, pattern="^(usdt|gift)$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, messages))
    print("🤖 Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
