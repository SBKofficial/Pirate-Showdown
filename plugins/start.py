import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes
from database import get_player, load_player, save_player
from utils import get_stats_text, MEDIA, DATA, generate_char_instance

logger = logging.getLogger(__name__)

async def show_starter_page(update, name, target_user_id):
    text = get_stats_text(name)
    # Pull File ID from media_assets.json
    img = MEDIA["IMAGES"].get(name, MEDIA["IMAGES"]["Default"])
    
    order = ["Usopp", "Nami", "Helmeppo"]
    if name not in order: name = "Usopp"
    idx = order.index(name)

    btns = [[InlineKeyboardButton(f"Choose {name} 🏴‍☠️", callback_data=f"choose_{name}_{target_user_id}")]]
    nav = []
    if idx > 0: nav.append(InlineKeyboardButton("⬅ Previous", callback_data=f"start_{order[idx-1]}_{target_user_id}"))
    if idx < len(order) - 1: nav.append(InlineKeyboardButton("Next ➡", callback_data=f"start_{order[idx+1]}_{target_user_id}"))
    btns.append(nav)
    
    markup = InlineKeyboardMarkup(btns)

    try:
        if update.callback_query:
            await update.callback_query.edit_message_media(InputMediaPhoto(img, caption=text, parse_mode="Markdown"), reply_markup=markup)
        else:
            await update.message.reply_photo(img, caption=text, reply_markup=markup, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Failed to load image for {name}: {e}")
        fallback_text = f"{text}\n\n⚠️ _(Image failed to load)_"
        if update.callback_query:
            await update.callback_query.edit_message_text(fallback_text, reply_markup=markup, parse_mode="Markdown")
        else:
            await update.message.reply_text(fallback_text, reply_markup=markup, parse_mode="Markdown")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    p = get_player(user_id, update.effective_user.first_name)

    # Referral system
    if context.args and not load_player(user_id):
        ref_id = str(context.args[0])
        if ref_id != str(user_id):
            referrer = get_player(ref_id)
            p['referred_by'] = ref_id
            p['berries'] += 5000
            referrer['berries'] += 10000
            save_player(ref_id, referrer)

    if p.get("starter_summoned"):
        await update.message.reply_text(f"Welcome back, Captain {p['name']}! Use /explore to set sail.")
        return

    await show_starter_page(update, "Usopp", user_id)

async def choose_starter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    _, name, uid = query.data.split("_")
    
    p = get_player(uid)
    if p.get("starter_summoned"):
        await query.answer("You've already set sail!", show_alert=True)
        return

    char = generate_char_instance(name)
    p["characters"] = [char]
    p["team"] = [char]
    p["starter_summoned"] = True
    save_player(uid, p)

    await query.edit_message_caption(caption=f"🏁 **{name} has joined your crew!**\n\nYour journey on the Grand Line begins now. Use /explore to find enemies!", parse_mode="Markdown")

def register(application):
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(start, pattern="^start_"))
    application.add_handler(CallbackQueryHandler(choose_starter, pattern="^choose_"))
