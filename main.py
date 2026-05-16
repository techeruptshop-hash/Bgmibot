import logging
import asyncio
from flask import Flask, request, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = "8471398768:AAEhz1zWPuK_8OTSf5qmaiJcRdDtcBXtcaQ"
WEBHOOK_URL = "https://kavyansh.onrender.com"
ADMIN_IDS = [-7428034309]
ADMIN_USERNAMES = ["Kavyanshh2009"]

BGMI_IDS = {
    "500": [
        {
            "id": "5123456789",
            "level": "Level 42",
            "tier": "Gold III",
            "uc": "450 UC",
            "skins": "4 Gun Skins, 2 Outfits, 1 Parachute Skin",
            "price": "500",
            "image_url": "https://i.imgur.com/sampleA.jpg",
        },
    ],
    "1000": [
        {
            "id": "6123456789",
            "level": "Level 67",
            "tier": "Diamond I",
            "uc": "1100 UC",
            "skins": "12 Gun Skins, 5 Outfits, 2 Full Sets, 1 Vehicle Skin",
            "price": "1000",
            "image_url": "https://i.imgur.com/sampleB.jpg",
        },
    ],
    "2000": [
        {
            "id": "7123456789",
            "level": "Level 82",
            "tier": "Ace",
            "uc": "3200 UC",
            "skins": "25 Gun Skins, 10 Outfits, 5 Full Sets, 3 Vehicle Skins",
            "price": "2000",
            "image_url": "https://i.imgur.com/sampleC.jpg",
        },
    ],
    "5000": [
        {
            "id": "8123456789",
            "level": "Level 100",
            "tier": "Conqueror",
            "uc": "8500 UC",
            "skins": "50+ Gun Skins, 20+ Outfits, 10+ Full Sets, Rare Items",
            "price": "5000",
            "image_url": "https://i.imgur.com/sampleD.jpg",
        },
    ],
}

flask_app = Flask(__name__)
application = Application.builder().token(BOT_TOKEN).build()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    name = user.first_name or "Player"
    text = (
        f"🎮 *Welcome to BGMI ID Shop, {name}!*\n\n"
        "We sell premium BGMI accounts at affordable prices.\n"
        "All accounts are verified & safe! ✅\n\n"
        "What would you like to do?"
    )
    keyboard = [
        [InlineKeyboardButton("🛒 Buy BGMI ID", callback_data="buy_id")],
        [InlineKeyboardButton("📞 Contact Admin", callback_data="contact_admin")],
        [InlineKeyboardButton("❓ Help", callback_data="help")],
    ]
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text.lower().strip()
    greetings = ["hi", "hello", "hey", "hlo", "hii", "sup", "yo", "start"]
    if any(g in msg for g in greetings):
        await start(update, context)
    else:
        await update.message.reply_text("👋 Say *Hi* or type /start to get started!", parse_mode="Markdown")


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "buy_id":
        keyboard = [
            [InlineKeyboardButton("💰 Under ₹500", callback_data="budget_500")],
            [InlineKeyboardButton("💰 Under ₹1000", callback_data="budget_1000")],
            [InlineKeyboardButton("💰 Under ₹2000", callback_data="budget_2000")],
            [InlineKeyboardButton("💰 Under ₹5000", callback_data="budget_5000")],
            [InlineKeyboardButton("🔙 Back", callback_data="back_main")],
        ]
        await query.edit_message_text(
            "💸 *Select Your Budget:*\n\nWe'll show you the best available IDs in your range!",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data.startswith("budget_"):
        budget = data.split("_")[1]
        ids = BGMI_IDS.get(budget, [])

        if not ids:
            await query.edit_message_text(
                "😔 *No IDs available in this budget right now.*\n\nPlease check back later or contact admin!",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📞 Contact Admin", callback_data="contact_admin")],
                    [InlineKeyboardButton("🔙 Back", callback_data="buy_id")],
                ])
            )
            return

        await query.edit_message_text(
            f"✅ *Showing IDs under ₹{budget}*\n\nScroll down to see all available accounts 👇",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back to Budgets", callback_data="buy_id")]
            ])
        )

        for i, acc in enumerate(ids, 1):
            caption = (
                f"🎮 *BGMI Account #{i}*\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"🆔 ID: `{acc['id']}`\n"
                f"📊 Level: {acc['level']}\n"
                f"🏆 Rank: {acc['tier']}\n"
                f"💎 UC: {acc['uc']}\n"
                f"🎨 Skins: {acc['skins']}\n"
                f"💰 Price: ₹{acc['price']}\n"
                f"━━━━━━━━━━━━━━━━"
            )
            keyboard = [[InlineKeyboardButton("📞 Buy This - Contact Admin", callback_data=f"contact_{budget}_{i-1}")]]
            try:
                await context.bot.send_photo(
                    chat_id=query.message.chat_id,
                    photo=acc["image_url"],
                    caption=caption,
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            except Exception:
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text=caption,
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )

    elif data.startswith("contact_") and data != "contact_admin":
        parts = data.split("_")
        budget = parts[1]
        idx = int(parts[2])
        acc = BGMI_IDS.get(budget, [])[idx]
        user = query.from_user

        admin_msg = (
            f"🔔 *New Customer Alert!*\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"👤 Name: {user.first_name}\n"
            f"🆔 Username: @{user.username or 'No username'}\n"
            f"💰 Budget: ₹{budget}\n"
            f"🎮 Interested In: ID `{acc['id']}`\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"Reply quickly! 🚀"
        )
        for admin_id in ADMIN_IDS:
            try:
                await context.bot.send_message(chat_id=admin_id, text=admin_msg, parse_mode="Markdown")
            except Exception as e:
                logger.error(f"Could not notify admin {admin_id}: {e}")

        admin_buttons = [
            [InlineKeyboardButton(f"💬 Chat with @{u}", url=f"https://t.me/{u}")]
            for u in ADMIN_USERNAMES
        ]
        admin_buttons.append([InlineKeyboardButton("🔙 Back to Menu", callback_data="back_main")])

        await query.edit_message_text(
            "✅ *Admin has been notified!*\n\nClick below to chat with admin directly 👇\n\n_Please mention which account you are interested in._",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(admin_buttons)
        )

    elif data == "contact_admin":
        admin_buttons = [
            [InlineKeyboardButton(f"💬 Chat with @{u}", url=f"https://t.me/{u}")]
            for u in ADMIN_USERNAMES
        ]
        admin_buttons.append([InlineKeyboardButton("🔙 Back", callback_data="back_main")])
        await query.edit_message_text(
            "📞 *Contact Our Admin:*\n\nClick below to directly message our admin!",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(admin_buttons)
        )

    elif data == "help":
        await query.edit_message_text(
            "❓ *Help & FAQ*\n\n"
            "🔹 *How to buy?*\n"
            "Tap Buy BGMI ID → Select budget → Choose account → Contact Admin\n\n"
            "🔹 *Is it safe?*\n"
            "Yes! All accounts are verified before listing.\n\n"
            "🔹 *Payment methods?*\n"
            "UPI, Paytm, GPay — ask admin for details.\n\n"
            "🔹 *Need help?*\n"
            "Contact admin directly anytime!",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📞 Contact Admin", callback_data="contact_admin")],
                [InlineKeyboardButton("🔙 Back", callback_data="back_main")],
            ])
        )

    elif data == "back_main":
        keyboard = [
            [InlineKeyboardButton("🛒 Buy BGMI ID", callback_data="buy_id")],
            [InlineKeyboardButton("📞 Contact Admin", callback_data="contact_admin")],
            [InlineKeyboardButton("❓ Help", callback_data="help")],
        ]
        await query.edit_message_text(
            "🎮 *BGMI ID Shop*\n\nWhat would you like to do?",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button_handler))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))


@flask_app.route("/")
def home():
    return "BGMI Bot is running!", 200


@flask_app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)
    asyncio.run(application.initialize())
    asyncio.run(application.process_update(update))
    return "OK", 200


@flask_app.route("/setwebhook")
def set_webhook():
    asyncio.run(application.bot.set_webhook(url=f"{WEBHOOK_URL}/webhook"))
    return "Webhook set successfully!", 200


if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=10000)
