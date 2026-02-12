from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, ContextTypes, CallbackQueryHandler
from database import get_player
from utils import MEDIA, get_required_player_exp, get_bar

async def inventory_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shows the user's primary currency and level status."""
    uid = update.effective_user.id
    p = get_player(uid)
    lvl = p.get('level', 1)
    req = get_required_player_exp(lvl)
    exp = p.get('exp', 0)
    
    # Visualizing level progress
    bar = get_bar(exp, req)
    
    text = (
        f"📦 **TREASURY: {p['name']}**\n\n"
        f"💰 **Berries:** 🍇{p.get('berries', 0):,}\n"
        f"🍀 **Clovers:** {p.get('clovers', 0):,}\n"
        f"🧩 **Tokens:** {p.get('tokens', 0):,}\n\n"
        f"🌟 **Level:** {lvl}\n"
        f"`{bar}` ({exp}/{req} EXP)"
    )
    
    kb = [
        [InlineKeyboardButton("View Collection 👤", callback_data="my_collection")],
        [InlineKeyboardButton("Equipped Team ⚔️", callback_data="my_team")]
    ]
    
    img = MEDIA["IMAGES"].get("INVENTORY", MEDIA["IMAGES"]["Default"])
    await update.message.reply_photo(img, caption=text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

async def my_collection_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Displays all pirates the user has recruited via the wheel."""
    query = update.callback_query
    uid = query.from_user.id
    p = get_player(uid)
    
    chars = p.get('characters', [])
    if not chars:
        await query.answer("Your collection is empty! Spin the /wheel first.", show_alert=True)
        return
        
    text = "👤 **YOUR RECRUITS**\n\n"
    for c in chars:
        text += f"• {c['name']} (Lv.{c['level']})\n"
        
    kb = [[InlineKeyboardButton("« Back", callback_data="back_to_inv")]]
    await query.edit_message_caption(caption=text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

async def back_to_inv_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Returns the user to the main inventory screen."""
    # Logic to refresh the main inventory view
    query = update.callback_query
    uid = query.from_user.id
    p = get_player(uid)
    lvl = p.get('level', 1)
    req = get_required_player_exp(lvl)
    exp = p.get('exp', 0)
    
    text = (f"📦 **TREASURY: {p['name']}**\n\n💰 **Berries:** 🍇{p.get('berries', 0):,}\n"
            f"🍀 **Clovers:** {p.get('clovers', 0):,}\n🌟 **Level:** {lvl}\n`{get_bar(exp, req)}`")
            
    kb = [[InlineKeyboardButton("View Collection 👤", callback_data="my_collection")]]
    await query.edit_message_caption(caption=text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

def register(application):
    application.add_handler(CommandHandler("inventory", inventory_cmd))
    application.add_handler(CommandHandler("myprofile", inventory_cmd))
    application.add_handler(CallbackQueryHandler(my_collection_callback, pattern="^my_collection$"))
    application.add_handler(CallbackQueryHandler(back_to_inv_callback, pattern="^back_to_inv$"))
