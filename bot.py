import sys
import os
import logging

# =====================
# PATH FIXING
# =====================
# This ensures Python can find config.py, database.py, and the plugins folder
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telegram.ext import ApplicationBuilder
from telegram import BotCommand
from config import Config
from loader import load_plugins

# =====================
# LOGGING SETUP
# =====================
# We use sys.stdout so logs appear instantly in the Stackhost console
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# =====================
# TELEGRAM COMMAND MENU
# =====================
async def post_init(application):
    """
    Registers the command list with Telegram's servers so they appear in the UI.
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
    
    # Check if Config is actually receiving the Token
    if not Config.BOT_TOKEN:
        logger.error("❌ CRITICAL: BOT_TOKEN is None! Check Stackhost Env Variables.")
        sys.exit(1)
    
    logger.info(f"Connecting to Telegram with token prefix: {Config.BOT_TOKEN[:10]}...")

    # Initialize Application
    application = (
        ApplicationBuilder()
        .token(Config.BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    # Automatically load all modules in the /plugins folder
    try:
        load_plugins(application)
    except Exception as e:
        logger.error(f"❌ Plugin Loading Error: {e}")

    logger.info("🏴‍☠️ Pirate Bot is modular and sailing!...")
    
    # Start Polling
    application.run_polling()
