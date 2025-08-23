import asyncio
import logging
from telegram import Update, Bot
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram.error import Forbidden

# ---------------- CONFIG ----------------
BOT_TOKEN = "8048782271:AAGZx7hIdRD3K6fUfqQ-WQab6DLunKcN4BY"
OWNER_ID = 5300776959
GROUP_ID = -1002739374681

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ---------------- WEBHOOK ----------------
async def clear_webhook():
    bot = Bot(token=BOT_TOKEN)
    await bot.delete_webhook()
    logger.info("Webhook cleared, safe to start polling.")

# ---------------- ALERTS ----------------
async def send_message_safe(application, chat_id, msg):
    try:
        await application.bot.send_message(chat_id=chat_id, text=msg, parse_mode=ParseMode.MARKDOWN)
    except Forbidden:
        logger.warning(f"Cannot send message to chat_id {chat_id} - bot blocked or removed.")

async def send_swing_alert(application):
    msg = (
        "*Swing Trading Alert*\n"
        "Stock: ABC\nEntry: 123\nSL: 120\nTarget: 135\nReason: Breakout + Volume Spike"
    )
    await send_message_safe(application, OWNER_ID, msg)
    await send_message_safe(application, GROUP_ID, msg)

async def send_delivery_alert(application):
    msg = "*Delivery % Spike Alert*\nStock: XYZ\nDelivery: 85%\nReason: Heavy institutional buying"
    await send_message_safe(application, OWNER_ID, msg)
    await send_message_safe(application, GROUP_ID, msg)

async def send_insider_alert(application):
    msg = "*Insider Activity Alert*\nStock: PQR\nBuyer: Promoter\nQuantity: 1,00,000"
    await send_message_safe(application, OWNER_ID, msg)
    await send_message_safe(application, GROUP_ID, msg)

async def send_weekly_summary(application):
    msg = "*Weekly Top Gainers*\n1. ABC\n2. XYZ\n3. PQR"
    await send_message_safe(application, OWNER_ID, msg)
    await send_message_safe(application, GROUP_ID, msg)

# ---------------- COMMAND HANDLERS ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot running ✅ Use /help to see commands.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "/start - Start bot\n"
        "/help - Show this help\n"
        "/swing - Get latest swing trading alert\n"
        "/delivery - Delivery % spike alert\n"
        "/insider - Insider activity alert\n"
        "/weekly - Weekly top gainers summary"
    )
    await update.message.reply_text(help_text)

async def swing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_swing_alert(context.application)

async def delivery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_delivery_alert(context.application)

async def insider(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_insider_alert(context.application)

async def weekly(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_weekly_summary(context.application)

# ---------------- SCHEDULE ALERTS ----------------
async def schedule_alerts(application):
    loop = asyncio.get_running_loop()
    scheduler = AsyncIOScheduler(event_loop=loop, timezone="Asia/Kolkata")
    scheduler.add_job(lambda: asyncio.create_task(send_swing_alert(application)), trigger='cron', hour=9, minute=20)
    scheduler.add_job(lambda: asyncio.create_task(send_delivery_alert(application)), trigger='cron', hour=11, minute=0)
    scheduler.add_job(lambda: asyncio.create_task(send_insider_alert(application)), trigger='cron', hour=12, minute=30)
    scheduler.add_job(lambda: asyncio.create_task(send_weekly_summary(application)), trigger='cron', day_of_week='fri', hour=15, minute=30)
    scheduler.start()
    logger.info("Scheduled alerts set.")

# ---------------- MAIN ----------------
async def main():
    await clear_webhook()

    application = Application.builder().token(BOT_TOKEN).job_queue(None).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("swing", swing))
    application.add_handler(CommandHandler("delivery", delivery))
    application.add_handler(CommandHandler("insider", insider))
    application.add_handler(CommandHandler("weekly", weekly))

    await schedule_alerts(application)

    await application.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
