import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, ContextTypes
from utils import MEDIA

async def explore(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Randomly pick an NPC from your provided list in media_assets
    npc_list = list(MEDIA["EXPLORE_DATA"].keys())
    enemy_name = random.choice(npc_list)
    enemy_img = MEDIA["EXPLORE_DATA"][enemy_name]
    
    text = (
        "🧭 **Grand Line Exploration**\n\n"
        f"You dropped anchor at a mysterious island and encountered **{enemy_name}**!"
    )
    
    kb = [[InlineKeyboardButton(f"Battle {enemy_name} ⚔️", callback_data=f"efight_{enemy_name}")]]
    
    await update.message.reply_photo(
        photo=enemy_img,
        caption=text,
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="Markdown"
    )

def register(application):
    application.add_handler(CommandHandler("explore", explore))
