from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes
from database import get_player, load_player, save_player
from utils import get_stats_text, DATA, MEDIA

async def show_starter_page(update, name, target_user_id):
    """Displays the pirate selection carousel."""
    text = get_stats_text(name)
    # Corrected key: IMAGES (matches your Media_assets.json)
    img = MEDIA["IMAGES"].get(name, MEDIA["IMAGES"].get("Default"))
    
    order = ["Usopp", "Nami", "Helmeppo"]
    if name not in order: name = "Usopp"
    idx = order.index(name)

    btns = [[InlineKeyboardButton("Choose this Pirate", callback_data=f"choose_{name}_{target_user_id}")]]
    nav = []
    if idx > 0: nav.append(InlineKeyboardButton("⬅ Previous", callback_data=f"start_{order[idx-1]}_{target_user_id}"))
    if idx < len(order) - 1: nav.append(InlineKeyboardButton("Next ➡", callback_data=f"start_{order[idx+1]}_{target_user_id}"))
    btns.append(nav)
    markup = InlineKeyboardMarkup(btns)

    if update.callback_query:
        await update.callback_query.edit_message_media(InputMediaPhoto(img, caption=text), reply_markup=markup)
    else:
        await update.message.reply_photo(img, caption=text, reply_markup=markup)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    p = get_player(user_id, update.effective_user.first_name)

    # Referral Logic
    if context.args and not load_player(user_id) and not p.get('referred_by'):
        ref_id = str(context.args[0])
        if ref_id != str(user_id):
            referrer = get_player(ref_id)
            p['referred_by'] = ref_id
            p['berries'] += 5000
            referrer['berries'] += 10000
            save_player(user_id, p)
            save_player(ref_id, referrer)

    if p.get("starter_summoned"):
        await update.message.reply_text(f"Welcome back, Captain {p['name']}!")
        return

    await show_starter_page(update, "Usopp", user_id)

def register(application):
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(start, pattern="^start_"))
