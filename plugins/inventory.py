import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, ContextTypes
from database import get_player
from utils import MEDIA

logger = logging.getLogger(__name__)

async def show_inventory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Displays the player's current currency, items, and crew."""
    user_id = update.effective_user.id
    p = get_player(user_id)
    
    # Inventory Image from media_assets.json
    img = MEDIA["IMAGES"].get("INVENTORY", MEDIA["IMAGES"]["Default"])
    
    # UI Text for the inventory
    text = (
        f"🎒 **{p['name']}'s Inventory**\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"💰 **Berries**: {p.get('berries', 0):,}\n"
        f"🍀 **Clovers**: {p.get('clovers', 0)}\n\n"
        f"🏴‍☠️ **Crew Size**: {len(p.get('characters', []))}\n"
        f"🏆 **Bosses Defeated**: {p.get('missions_completed', 0)}\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "Use /team to manage your crew or /shop to spend Berries!"
    )
    
    btns = [
        [InlineKeyboardButton("View Crew 👥", callback_data="view_crew")],
        [InlineKeyboardButton("Close ❌", callback_data="close_menu")]
    ]
    
    await update.message.reply_photo(
        photo=img,
        caption=text,
        reply_markup=InlineKeyboardMarkup(btns),
        parse_mode="Markdown"
    )

def register(application):
    application.add_handler(CommandHandler("inventory", show_inventory))
    application.add_handler(CommandHandler("bag", show_inventory))
