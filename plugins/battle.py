import random
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaVideo
from telegram.ext import CallbackQueryHandler, ContextTypes
from utils import DATA, MEDIA, get_bar

logger = logging.getLogger(__name__)

async def start_battle(update, context, enemy_name, is_boss=False):
    query = update.callback_query
    uid = query.from_user.id
    # In a full system, you'd pull the player's active team from MongoDB here
    
    text = f"⚔️ **Battle Started!**\n\nYou are facing **{enemy_name}**!"
    
    # UI Buttons for moves
    btns = [
        [InlineKeyboardButton("Strike 👊", callback_data=f"attack_strike_{enemy_name}")],
        [InlineKeyboardButton("Use Ultimate 🔥", callback_data=f"attack_ult_{enemy_name}")]
    ]
    
    await query.edit_message_caption(caption=text, reply_markup=InlineKeyboardMarkup(btns), parse_mode="Markdown")

async def handle_attack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    _, move_name, enemy = query.data.split("_")
    
    # Check if this is a special ultimate with a video animation
    if move_name == "ult":
        # Example for Yamato/Kid animations provided in your data
        if "Yamato" in enemy:
            video = MEDIA["VIDEOS"]["YAMATO_ULT"]
            await query.edit_message_media(InputMediaVideo(video, caption="❄️ **YAMATO USES THUNDER BAGUA!**"))
        elif "Kid" in enemy:
            video = MEDIA["VIDEOS"]["KID_ULT"]
            await query.edit_message_media(InputMediaVideo(video, caption="⚡️ **KID USES DAMNED PUNK!**"))

    # Logic for damage calculation would go here using DATA["MOVES"]
    dmg = DATA["MOVES"].get(move_name, {"dmg": 30})["dmg"]
    
    await query.answer(f"Dealt {dmg} damage to {enemy}!", show_alert=False)

def register(application):
    application.add_handler(CallbackQueryHandler(start_battle, pattern="^efight_|^bfight_"))
    application.add_handler(CallbackQueryHandler(handle_attack, pattern="^attack_"))
