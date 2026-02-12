from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, ContextTypes
from database import get_player, load_player
from utils import MEDIA, get_required_player_exp

async def inventory_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    p = get_player(uid)
    lvl = p.get('level', 1)
    req = get_required_player_exp(lvl)
    
    inv = (f"📦 **INVENTORY**\n\nName: {p['name']}\n"
           f"Berries: 🍇{p.get('berries', 0):,}\n"
           f"Clovers: 🍀{p.get('clovers', 0):,}\n"
           f"Level: {lvl} ({p.get('exp', 0)}/{req} EXP)")
    
    kb = [[InlineKeyboardButton("Weapons ⚔️", callback_data="inv_weapons"), 
           InlineKeyboardButton("Fruits 🍎", callback_data="inv_fruits")]]
    await update.message.reply_photo(MEDIA["IMAGES"]["INVENTORY"], caption=inv, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

def register(application):
    application.add_handler(CommandHandler("inventory", inventory_cmd))
