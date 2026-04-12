from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
import configparser
import logging
from ChatGPT_HKBU import ChatGPT
from DBUtil import save_chat_history, get_recent_chat_history
import pymongo
import asyncio
import datetime


gpt = None
bot_config = None
config = None

async def send_reminder_after_delay(bot, chat_id, minutes):
    try:
        await asyncio.sleep(minutes * 60)
        await bot.send_message(
            chat_id=chat_id,
            text="Hey, it’s been a while.\nI’m still here if you want to talk 💛"
        )
    except asyncio.CancelledError:
        pass

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = """
Hi! I am your gentle and empathetic emotional support companion.

I am here to listen carefully, without judgment.
You can talk to me about breakups, exam failure, stress, sadness, or any difficult thoughts.

If you ever feel overwhelmed, I will gently encourage you to seek help and stay alive.

You can use these commands:
/start - Restart & read my role again
/help  - See examples of how to talk to me
/history - View your recent mood summary  
"""
    await update.message.reply_text(welcome_text)

    chat_id = update.effective_chat.id
    if 'reminder_task' in context.user_data:
        context.user_data['reminder_task'].cancel()
    task = asyncio.create_task(send_reminder_after_delay(context.bot, chat_id, 1))
    context.user_data['reminder_task'] = task

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
📌 How to talk to your emotional support bot:
Just send me a message about how you feel. I will always be kind to you.

💡 Examples of what you can say:
- "I failed my exam and I feel so stupid."
- "My partner broke up with me, I don't know what to do."
- "I've been stressed about school all week."
- "Sometimes I feel like no one understands me."
- "I have dark thoughts and I want to hurt myself."

If you ever talk about self-harm or suicide, I will gently ask you to reach out for professional help.

Commands:
/start - See my role introduction
/help  - Show this help message
/history - View your recent mood summary
"""
    await update.message.reply_text(help_text)

async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
   
    loading_msg = await update.message.reply_text("🔍 I’m preparing your recent mood summary...")

    user_id = str(update.effective_user.id)
    records = get_recent_chat_history(config, user_id, 3)

    if not records:
        await loading_msg.delete()
        await update.message.reply_text("You don’t have any chat history yet~")
        return

    history_text = ""
    for idx, record in enumerate(records):
      
        q = record.get("user_message", "")
        a = record.get("bot_response", "")
        history_text += f"\n=== Chat {idx+1} ===\nYou: {q}\nBot: {a}\n"

    prompt = f"""
You are a gentle emotional support companion.
Please give a short, warm summary of the user's mood based on the recent 3 chats.
Keep it soft, understanding, and encouraging.
Do NOT use bullet points.
Use simple English.

Chat History:
{history_text}

Summary:
"""

    summary = gpt.submit(prompt)

    await loading_msg.delete()
    await update.message.reply_text(f"✨ Your Recent Mood Summary ✨\n\n{summary}")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if 'reminder_task' in context.user_data:
        context.user_data['reminder_task'].cancel()
    task = asyncio.create_task(send_reminder_after_delay(context.bot, chat_id, 1))
    context.user_data['reminder_task'] = task

    thinking_msg = await update.message.reply_text("thinking...")
    user_text = update.message.text.strip()
    user_id = str(update.effective_user.id)
    
    reply = gpt.submit(user_text)
    save_chat_history(config, user_id, user_text, reply)

    await thinking_msg.delete()
    await update.message.reply_text(reply)

def main():
    global gpt, bot_config, config

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    logging.info('INIT: Loading configuration...')
    config = configparser.ConfigParser()
    config.read('config.ini')

    client = pymongo.MongoClient(config['MONGODB']['URI'])
    db = client[config['MONGODB']['DB_NAME']]
    bot_config = db['bot_config'].find_one()
    gpt = ChatGPT(config)

    logging.info('INIT: Starting Telegram bot...')
    application = ApplicationBuilder().token(config['TELEGRAM']['ACCESS_TOKEN']).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("history", history_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    application.run_polling()

if __name__ == '__main__':
    main()