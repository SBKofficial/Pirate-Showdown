import sys
import os
import logging

# =====================
# PATH FIXING
# =====================
# This ensures Python can find config.py, database.py, etc., on Stackhost
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telegram.ext import ApplicationBuilder
from telegram import BotCommand
from config import Config
from loader import load_plugins

# =====================
# LOGGING SETUP
# =====================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    stream=sys.stdout  # Force logs to show in Stackhost console
)
logger = logging.getLogger(__name__)

# =====================
# TELEGRAM COMMAND MENU
# =====================
async def post_init(application):
    """
    This function runs once when the bot starts.
    It uploads the command list to Telegram so they appear in the menu.
    """
    commands = [
        BotCommand("start", "Start your pirate journey"),
        BotCommand("explore", "Explore the Grand Line"),
        BotCommand("battle", "Fight other pirates"),
        BotCommand("inventory", "Check your treasury"),
        BotCommand("store", "Open the black market"),
        BotCommand("myteam", "Manage your active team"),
        BotCommand("mycollection", "View your recruited pirates"),
        BotCommand("wheel", "Summon new pirates/items"),
        BotCommand("myprofile", "View your pirate status"),
        BotCommand("referral", "Get your invite link")
    ]
    await application.bot.set_my_commands(commands)
    logger.info("✅ Bot commands have been uploaded to Telegram.")

# =====================
# MAIN EXECUTION
# =====================
if __name__ == "__main__":
    print("--- PIRATE BOT BOOTING UP ---")
    
    if not Config.BOT_TOKEN:
        logger.error("❌ Error: BOT_TOKEN is missing! Check your Stackhost environment variables.")
        sys.exit(1)

    # Initialize the Application
    application = ApplicationBuilder().token(Config.BOT_TOKEN).post_init(post_init).build()

    # Automatically load all files from the /plugins folder
    try:
        load_plugins(application)
    except Exception as e:
        logger.error(f"❌ Failed to load plugins: {e}")

    logger.info("🏴‍☠️ Pirate Bot is modular and sailing!...")
    application.run_polling()
