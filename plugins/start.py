from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes
from database import get_player, load_player, save_player
from utils import get_stats_text, DATA, MEDIA

async def show_starter_page(update, name, target_user_id):
    text = get_stats_text(name)
    # Fixed the key from IMAGE_URLS to IMAGES to match your JSON
    img = MEDIA["IMAGES"].get(name, MEDIA.get("IMAGES", {}).get("Default", ""))
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
    existing_player = load_player(user_id)
    p = get_player(user_id, update.effective_user.first_name)

    if context.args and not existing_player and not p.get('referred_by'):
        referrer_id = str(context.args[0])
        if referrer_id != str(user_id):
            referrer = load_player(referrer_id)
            if referrer:
                p['referred_by'], p['berries'], p['clovers'] = referrer_id, p.get('berries', 0)+5000, p.get('clovers', 0)+50
                referrer['berries'], referrer['clovers'] = referrer.get('berries',0)+10000, referrer.get('clovers',0)+100
                referrer['referrals'] = referrer.get('referrals', 0) + 1
                save_player(user_id, p); save_player(referrer_id, referrer)
                await update.message.reply_text(f"🤝 Referred by {referrer['name']}! +5,000 🍇, +50 🍀")

    if p.get("starter_summoned"):
        await update.message.reply_text(f"Welcome back Captain {p['name']}!")
        return

    await show_starter_page(update, "Usopp", user_id)

def register(application):
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(start, pattern="^start_"))
