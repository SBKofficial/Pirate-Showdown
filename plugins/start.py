import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from database import get_player, load_player, save_player
from utils import get_stats_text, DATA, MEDIA, generate_char_instance

logger = logging.getLogger(__name__)

# =====================
# ID CATCHER LOGIC
# =====================
async def catch_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Replies with the File ID of any photo or video sent to the bot."""
    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        await update.message.reply_text(f"📸 **Photo File ID:**\n<code>{file_id}</code>", parse_mode="HTML")
    elif update.message.video:
        file_id = update.message.video.file_id
        await update.message.reply_text(f"🎥 **Video File ID:**\n<code>{file_id}</code>", parse_mode="HTML")

# =====================
# STARTER MENU LOGIC
# =====================
async def show_starter_page(update, name, target_user_id):
    """Handles the selection carousel."""
    text = get_stats_text(name)
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

    try:
        if update.callback_query:
            if img:
                await update.callback_query.edit_message_media(InputMediaPhoto(img, caption=text), reply_markup=markup)
            else:
                await update.callback_query.edit_message_text(text, reply_markup=markup)
        else:
            if img:
                await update.message.reply_photo(img, caption=text, reply_markup=markup)
            else:
                await update.message.reply_text(text, reply_markup=markup)
    except Exception as e:
        logger.error(f"Image error for {name}: {e}")
        if update.message: await update.message.reply_text(f"{text}\n\n⚠️ Image failed.", reply_markup=markup)

# =====================
# CHOICE & REFERRAL LOGIC
# =====================
async def choose_starter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Saves the chosen pirate to the database."""
    query = update.callback_query
    _, name, uid = query.data.split("_")
    
    p = get_player(uid)
    if p.get("starter_summoned"):
        await query.answer("You already have a starter!", show_alert=True)
        return

    starter_char = generate_char_instance(name, level=1)
    p["characters"] = [starter_char]
    p["team"] = [starter_char]
    p["starter_summoned"] = True
    save_player(uid, p)

    await query.edit_message_caption(
        caption=f"🏴‍☠️ **Excellent choice, Captain!**\n\n{name} has joined your crew. Use /explore to begin!",
        parse_mode="Markdown"
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    p = get_player(user_id, update.effective_user.first_name)

    # [span_0](start_span)Referral system: 10k Berries for the recruiter[span_0](end_span)
    if context.args and not load_player(user_id) and not p.get('referred_by'):
        ref_id = str(context.args[0])
        if ref_id != str(user_id):
            referrer = get_player(ref_id)
            p['referred_by'] = ref_id
            p['berries'] = p.get('berries', 0) + 5000
            referrer['berries'] = referrer.get('berries', 0) + 10000
            save_player(user_id, p)
            save_player(ref_id, referrer)

    if p.get("starter_summoned"):
        await update.message.reply_text(f"Welcome back, Captain {p['name']}!")
        return

    await show_starter_page(update, "Usopp", user_id)

def register(application):
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(start, pattern="^start_"))
    application.add_handler(CallbackQueryHandler(choose_starter, pattern="^choose_"))
    application.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, catch_id))
