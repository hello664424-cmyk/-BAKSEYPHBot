import os
import logging
import requests
from telegram import Update, BotCommand
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Logging configuration
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Retrieve environment variables
TOKEN = os.getenv("BOT_TOKEN")

async def post_init(application):
    """Set bot commands menu dynamically on startup."""
    commands = [
        BotCommand("start", "Start the bot and get instructions"),
        BotCommand("help", "How to use this bot"),
        BotCommand("about", "About this bot"),
    ]
    await application.bot.set_my_commands(commands)
    logger.info("Bot commands menu updated successfully.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcoming message upon /start command."""
    welcome_text = (
        "👋 **Welcome to TikTok Downloader Bot!**\n\n"
        "Send me any TikTok video link, and I will download it without watermark for you!"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send help instructions upon /help command."""
    help_text = (
        "📖 **How to use:**\n\n"
        "1. Copy a video link from TikTok.\n"
        "2. Paste and send the link here.\n"
        "3. Wait a few seconds for the video without watermark!"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send bot details upon /about command."""
    about_text = (
        "ℹ️ **TikTok Downloader Bot**\n\n"
        "Fast, simple, and free TikTok video downloader without watermark."
    )
    await update.message.reply_text(about_text, parse_mode="Markdown")

async def download_tiktok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming TikTok links."""
    text = update.message.text.strip()
    
    # Simple URL check
    if "tiktok.com" not in text:
        await update.message.reply_text("⚠️ Please send a valid TikTok video link.")
        return

    status_msg = await update.message.reply_text("⏳ Processing video... Please wait.")

    try:
        # Request data from TikWM API
        api_url = f"https://www.tikwm.com/api/?url={text}"
        response = requests.get(api_url, timeout=15)
        res_data = response.json()

        if res_data.get("code") == 0:
            data = res_data.get("data", {})
            video_url = data.get("play")  # Watermark-free video URL
            title = data.get("title", "TikTok Video")

            if video_url:
                await status_msg.edit_text("📥 Uploading video to Telegram...")
                await update.message.reply_video(
                    video=video_url,
                    caption=f"🎬 **{title}**\n\n✨ Downloaded via Bot",
                    parse_mode="Markdown"
                )
                await status_msg.delete()
            else:
                await status_msg.edit_text("❌ Could not extract video URL.")
        else:
            await status_msg.edit_text("❌ Failed to fetch video. Please ensure the link is public.")

    except Exception as e:
        logger.error(f"Error downloading TikTok video: {e}")
        await status_msg.edit_text("❌ An error occurred while processing your request.")

def main():
    if not TOKEN:
        raise ValueError("BOT_TOKEN environment variable is not set.")

    # Initialize Application with post_init hook
    app = ApplicationBuilder().token(TOKEN).post_init(post_init).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("about", about_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_tiktok))

    # Start Polling
    logger.info("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
