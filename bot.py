import logging
from telegram.ext import ApplicationBuilder, CallbackQueryHandler
from config import Config
from loader import load_plugins
from database import load_player

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def post_init(application):
    # This automatically sets the command menu in Telegram
    from telegram import BotCommand
    await application.bot.set_my_commands([
        BotCommand("start", "Start your journey"),
        BotCommand("explore", "Explore the Grand Line"),
        BotCommand("battle", "Challenge a pirate"),
        BotCommand("inventory", "Check your treasury"),
        BotCommand("store", "Open the store")
    ])

if __name__ == "__main__":
    if not Config.BOT_TOKEN:
        print("❌ Error: BOT_TOKEN is missing!")
        exit(1)

    # Build Application
    application = ApplicationBuilder().token(Config.BOT_TOKEN).post_init(post_init).build()

    # Load all plugins from the /plugins folder
    load_plugins(application)

    print("🏴‍☠️ Pirate Bot is modular and sailing!...")
    application.run_polling()
