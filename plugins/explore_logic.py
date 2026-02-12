import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler, ContextTypes
from database import get_player, save_player
from utils import MEDIA

async def handle_explore_rewards(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Logic for chest drops and berry finds during exploration."""
    query = update.callback_query
    uid = query.from_user.id
    p = get_player(uid)
    
    # 20% chance to find a chest
    chance = random.random()
    
    if chance < 0.20:
        # Pick a random chest from your media_assets
        chest_type = random.choice(["DARK", "GOLD", "FROST"])
        chest_img = MEDIA["IMAGES"]["CHESTS"][chest_type]
        
        text = f"🎁 **Loot Found!**\n\nYou discovered a **{chest_type} CHEST** while sailing!"
        kb = [[InlineKeyboardButton(f"Open {chest_type} Chest 🔑", callback_data=f"open_chest_{chest_type}")]]
        
        await query.edit_message_media(
            media=InputMediaPhoto(chest_img, caption=text, parse_mode="Markdown"),
            reply_markup=InlineKeyboardMarkup(kb)
        )
    else:
        # Normal Berry find
        found = random.randint(100, 500)
        p["berries"] += found
        save_player(uid, p)
        await query.answer(f"💰 Found {found} Berries on the shore!", show_alert=True)

async def open_chest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chest_type = query.data.split("_")[2]
    
    # Reward logic based on chest type
    reward = 1000 if chest_type == "GOLD" else 500
    
    await query.edit_message_caption(
        caption=f"🔓 **Chest Opened!**\n\nYou received **{reward} Berries** and a rare item!",
        parse_mode="Markdown"
    )

def register(application):
    application.add_handler(CallbackQueryHandler(open_chest, pattern="^open_chest_"))
