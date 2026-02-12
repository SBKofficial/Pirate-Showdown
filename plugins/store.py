from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, ContextTypes, CallbackQueryHandler
from database import get_player, load_player, save_player
from utils import DATA, MEDIA

async def store_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        await update.message.reply_text("⚠️ This command is DM only.")
        return
    
    text = "⚓️ **PIRATE STORE** ⚓️\n\nSelect a category to browse items."
    kb = [[InlineKeyboardButton("Weapons ⚔️", callback_data="store_weapons"), 
           InlineKeyboardButton("Fruits 🍎", callback_data="store_fruits")]]
    await update.message.reply_photo(MEDIA["IMAGES"]["STORE"], caption=text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

async def buy_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/buy Item Name`")
        return
    # Purchase logic here using DATA["WEAPONS"] and DATA["DEVIL_FRUITS"]...

def register(application):
    application.add_handler(CommandHandler("store", store_cmd))
    application.add_handler(CommandHandler("buy", buy_cmd))
