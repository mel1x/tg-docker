import os
import psycopg2
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

if os.path.exists('.env'):
    load_dotenv('.env')
elif os.path.exists('../.env'):
    load_dotenv('../.env')

BOT_TOKEN = os.getenv('BOT_TOKEN')
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'db'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD')
}


def connectDb():
    # return psycopg2.connect(**DB_CONFIG)

    conn = psycopg2.connect(**DB_CONFIG)
    conn.set_client_encoding('UTF8')
    return conn


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    conn = connectDb()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (user_id, username, first_name, last_name) "
        "VALUES (%s, %s, %s, %s) ON CONFLICT (user_id) DO NOTHING",
        (user.id, user.username or '', user.first_name or '', user.last_name or '')
    )
    conn.commit()
    cursor.close()
    conn.close()
    await update.message.reply_text("ÐŸÑ€Ð¸Ð²ÐµÑ‚! Ð¢Ñ‹ Ð·Ð°Ñ€ÐµÐ³Ð¸ÑÑ‚Ñ€Ð¸Ñ€Ð¾Ð²Ð°Ð½.")


async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not context.args:
        await update.message.reply_text("Ð˜ÑÐ¿Ð¾Ð»ÑŒÐ·Ð¾Ð²Ð°Ð½Ð¸Ðµ: /add <ÑÐ¾Ð¾Ð±Ñ‰ÐµÐ½Ð¸Ðµ>")
        return
    messageText = ' '.join(context.args)
    conn = connectDb()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO user_messages (user_id, username, message_text) VALUES (%s, %s, %s)",
        (user.id, user.username or '', messageText)
    )
    conn.commit()
    cursor.close()
    conn.close()
    await update.message.reply_text("Ð¡Ð¾Ð¾Ð±Ñ‰ÐµÐ½Ð¸Ðµ Ð´Ð¾Ð±Ð°Ð²Ð»ÐµÐ½Ð¾!")


async def read(update: Update, context: ContextTypes.DEFAULT_TYPE):
    page = 0
    if context.args:
        page = int(context.args[0])
    await showMessages(update, page)


async def showMessages(update: Update, page: int):
    conn = connectDb()
    cursor = conn.cursor()
    offset = page * 8
    cursor.execute(
        "SELECT id, message_text FROM user_messages ORDER BY id LIMIT 8 OFFSET %s",
        (offset,)
    )
    messages = cursor.fetchall()
    cursor.execute("SELECT COUNT(*) FROM user_messages")
    total = cursor.fetchone()[0]
    cursor.close()
    conn.close()

    if not messages:
        if update.callback_query:
            await update.callback_query.message.edit_text("ÐÐµÑ‚ ÑÐ¾Ð¾Ð±Ñ‰ÐµÐ½Ð¸Ð¹.")
        else:
            await update.message.reply_text("ÐÐµÑ‚ ÑÐ¾Ð¾Ð±Ñ‰ÐµÐ½Ð¸Ð¹.")
        return

    keyboard = []
    for msg in messages:
        msgId, text = msg
        shortText = text[:30] + "..." if len(text) > 30 else text
        keyboard.append([InlineKeyboardButton(shortText, callback_data=f"msg_{msgId}")])

    navButtons = []
    if page > 0:
        navButtons.append(InlineKeyboardButton("â¬…ï¸ ÐÐ°Ð·Ð°Ð´", callback_data=f"page_{page - 1}"))
    if offset + 8 < total:
        navButtons.append(InlineKeyboardButton("Ð’Ð¿ÐµÑ€ÐµÐ´ âž¡ï¸", callback_data=f"page_{page + 1}"))
    if navButtons:
        keyboard.append(navButtons)

    replyMarkup = InlineKeyboardMarkup(keyboard)
    text = f"Ð¡Ð¾Ð¾Ð±Ñ‰ÐµÐ½Ð¸Ñ (ÑÑ‚Ñ€Ð°Ð½Ð¸Ñ†Ð° {page + 1}):"

    if update.callback_query:
        await update.callback_query.message.edit_text(text, reply_markup=replyMarkup)
    else:
        await update.message.reply_text(text, reply_markup=replyMarkup)


async def buttonHandler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("msg_"):
        msgId = int(data.split("_")[1])
        conn = connectDb()
        cursor = conn.cursor()
        cursor.execute("SELECT message_text FROM user_messages WHERE id = %s", (msgId,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        if result:
            await query.message.reply_text(result[0])
    elif data.startswith("page_"):
        page = int(data.split("_")[1])
        await showMessages(update, page)


def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("read", read))
    app.add_handler(CallbackQueryHandler(buttonHandler))
    app.run_polling()


if __name__ == "__main__":
    main()
