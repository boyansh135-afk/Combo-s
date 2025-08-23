import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import requests
import json
import datetime

# ==== YOUR BOT CONFIGURATION ====
BOT_TOKEN = "8048782271:AAGZx7hIdRD3K6fUfqQ-WQab6DLunKcN4BY"
USER_ID = 5300776959
GROUP_ID = -1002739374681
WEBHOOK_URL = "https://your-render-url.onrender.com"  # Replace with your Render domain

# ==== LOGGING ====
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# ==== CHARTINK SCRAPER ====
def fetch_chartink_data():
    url = "https://chartink.com/screener/process"  # Replace with your screener endpoint if customized
    payload = {
        "scan_clause": "( {cash} ( latest close > 100 and latest close < 500 ) )"  # Example filter
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}
    response = requests.post(url, data=payload, headers=headers)
    if response.status_code == 200:
        try:
            data = response.json()
            stocks = [s["nsecode"] for s in data.get("data", [])]
            return stocks if stocks else ["No stocks found"]
        except json.JSONDecodeError:
            return ["Error decoding JSON"]
    return [f"Failed to fetch data: {response.status_code}"]

# ==== COMMAND HANDLER ====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot is running with Webhook + Daily Schedule + Chartink Scraper!")

# ==== DAILY SCHEDULED TASK ====
async def send_daily_alert(context: ContextTypes.DEFAULT_TYPE):
    stocks = fetch_chartink_data()
    message = f"📊 **Daily Stock Picks ({datetime.date.today()})**\n\n" + "\n".join(stocks)
    await context.bot.send_message(chat_id=USER_ID, text=message)
    await context.bot.send_message(chat_id=GROUP_ID, text=message)

# ==== MAIN FUNCTION ====
def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Command handlers
    application.add_handler(CommandHandler("start", start))

    # Scheduler for daily alerts (9:20 AM IST → 03:50 AM UTC)
    scheduler = AsyncIOScheduler(timezone="Asia/Kolkata")
    scheduler.add_job(send_daily_alert, trigger="cron", hour=9, minute=20, args=[application.bot])
    scheduler.start()

    # Webhook Setup
    application.run_webhook(
        listen="0.0.0.0",
        port=10000,
        url_path=BOT_TOKEN,
        webhook_url=f"{WEBHOOK_URL}/{BOT_TOKEN}",
    )

if __name__ == "__main__":
    main()
