from telegram import Update, ParseMode
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)
import logging
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# ------------------- CONFIG -------------------
BOT_TOKEN = "8048782271:AAGZx7hIdRD3K6fUfqQ-WQab6DLunKcN4BY"
OWNER_ID = 5300776959
GROUP_ID = -1002739374681

# ------------------- LOGGING -------------------
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ------------------- TRADING ALERT PLACEHOLDERS -------------------
async def send_swing_alert(application):
    message = (
        "*Swing Trading Alert*\n\n"
        "Stock: ABC\n"
        "Entry: 123\n"
        "SL: 120\n"
        "Target: 135\n"
        "Reason: Breakout + Volume Spike"
    )
    await application.bot.send_message(chat_id=OWNER_ID, text=message, parse_mode=ParseMode.MARKDOWN)
    await application.bot.send_message(chat_id=GROUP_ID, text=message, parse_mode=ParseMode.MARKDOWN)

async def send_delivery_alert(application):
    message = "*Delivery % Spike Alert*\nStock: XYZ\nDelivery: 85%\nReason: Heavy institutional buying"
    await application.bot.send_message(chat_id=OWNER_ID, text=message, parse_mode=ParseMode.MARKDOWN)
    await application.bot.send_message(chat_id=GROUP_ID, text=message, parse_mode=ParseMode.MARKDOWN)

async def send_insider_alert(application):
    message = "*Insider Activity Alert*\nStock: PQR\nBuyer: Promoter\nQuantity: 1,00,000"
    await application.bot.send_message(chat_id=OWNER_ID, text=message, parse_mode=ParseMode.MARKDOWN)
    await application.bot.send_message(chat_id=GROUP_ID, text=message, parse_mode=ParseMode.MARKDOWN)

async def send_weekly_summary(application):
    message = "*Weekly Top Gainers*\n1. ABC\n2. XYZ\n3. PQR"
    await application.bot.send_message(chat_id=OWNER_ID, text=message, parse_mode=ParseMode.MARKDOWN)
    await application.bot.send_message(chat_id=GROUP_ID, text=message, parse_mode=ParseMode.MARKDOWN)

# ------------------- COMMAND HANDLERS -------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Bot is running ✅ Use /help to see commands.")

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

# ------------------- SCHEDULED ALERTS -------------------
def schedule_alerts(application):
    """Schedules automatic alerts at exact times using AsyncIOScheduler."""
    scheduler = AsyncIOScheduler(timezone="Asia/Kolkata")  # IST timezone

    # Swing Picks - Daily at 9:20 AM
    scheduler.add_job(lambda: asyncio.create_task(send_swing_alert(application)),
                      trigger='cron', hour=9, minute=20, second=0)

    # Delivery % Spike - Daily at 11:00 AM
    scheduler.add_job(lambda: asyncio.create_task(send_delivery_alert(application)),
                      trigger='cron', hour=11, minute=0, second=0)

    # Insider / Bulk Deal - Daily at 12:30 PM
    scheduler.add_job(lambda: asyncio.create_task(send_insider_alert(application)),
                      trigger='cron', hour=12, minute=30, second=0)

    # Weekly Top Gainers - Friday at 3:30 PM
    scheduler.add_job(lambda: asyncio.create_task(send_weekly_summary(application)),
                      trigger='cron', day_of_week='fri', hour=15, minute=30, second=0)

    scheduler.start()
    logger.info("Scheduled alerts set for swing, delivery, insider, and weekly.")

# ------------------- MAIN FUNCTION -------------------
def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # ⚡ Patch JobQueue weakref issue for Python 3.13
    if application.job_queue:
        application.job_queue._application = application

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("swing", swing))
    application.add_handler(CommandHandler("delivery", delivery))
    application.add_handler(CommandHandler("insider", insider))
    application.add_handler(CommandHandler("weekly", weekly))

    # Start scheduled alerts at exact times
    schedule_alerts(application)

    # Run bot
    application.run_polling()

if __name__ == "__main__":
    main()
