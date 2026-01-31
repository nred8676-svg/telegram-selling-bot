import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ===== ENV VARIABLES =====
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
USDT_ADDRESS = os.getenv("USDT_ADDRESS", "Not Set")

# ===== /start =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💰 Price List", callback_data="price")],
        [InlineKeyboardButton("💬 Chat with Admin", callback_data="chat")],
        [InlineKeyboardButton("💳 Payment Method", callback_data="payment")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🌸 Welcome 🌸\n\nChoose an option below 👇",
        reply_markup=reply_markup
    )

# ===== BUTTON HANDLER =====
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "price":
        await query.message.reply_text(
            "📌 PRICE LIST\n\n"
            "• Telegram ID – ₹XXX\n"
            "• WhatsApp ID – ₹XXX\n"
            "• Combo – ₹XXX\n\n"
            "💬 Buy karne ke liye Admin ko msg karein"
        )

    elif query.data == "chat":
        await query.message.reply_text("💬 Apna message likho, admin tak pahunch jayega")

    elif query.data == "payment":
        await query.message.reply_text(
            "💳 PAYMENT METHODS\n\n"
            "✅ USDT (TRC20)\n"
            f"`{USDT_ADDRESS}`\n\n"
            "✅ Manual Trust Payment\n\n"
            "Payment ke baad screenshot bhejo 📸",
            parse_mode="Markdown"
        )

# ===== USER MESSAGE → ADMIN =====
async def user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # Agar admin hai to skip
    if user.id == ADMIN_ID:
        return

    user_id = user.id
    username = f"@{user.username}" if user.username else "Not Available"
    name = user.first_name or ""

    text = update.message.text

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            "👤 NEW USER MESSAGE\n\n"
            f"🆔 User ID: `{user_id}`\n"
            f"👤 Username: {username}\n"
            f"📛 Name: {name}\n\n"
            f"💬 Message:\n{text}"
        ),
        parse_mode="Markdown"
    )

    await update.message.reply_text("✅ Admin ko bhej diya gaya")

# ===== ADMIN REPLY → USER =====
async def admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if not update.message.reply_to_message:
        return

    text = update.message.text

    try:
        lines = update.message.reply_to_message.text.splitlines()
        user_id_line = [l for l in lines if "User ID" in l][0]
        user_id = int(user_id_line.split("`")[1])

        await context.bot.send_message(
            chat_id=user_id,
            text=f"👑 Admin Reply:\n\n{text}"
        )
    except Exception as e:
        await update.message.reply_text("❌ Reply failed")

# ===== MAIN =====
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & filters.REPLY, admin_reply))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, user_message))
    app.add_handler(MessageHandler(filters.UpdateType.CALLBACK_QUERY, button_handler))

    print("🤖 Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
