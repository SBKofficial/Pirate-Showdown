import random
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, ContextTypes
from database import get_player, load_player, save_player
from utils import MEDIA, DATA

pending_explores = {}

async def explore_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        await update.message.reply_text("⚠️ This command can only be used in private messages (DM).")
        return

    uid = str(update.effective_user.id)
    if not load_player(uid):
        await update.message.reply_text("⚠️ You must start your journey first! Use /start.")
        return

    p = get_player(uid)
    
    # Cooldown logic
    if uid in pending_explores:
        last_time = pending_explores[uid].get('time', 0)
        if time.time() - last_time < 120:
            remaining = int(120 - (time.time() - last_time))
            await update.message.reply_text(f"⚠️ You have an unfinished battle! Escape and explore again in {remaining} seconds.")
            return

    p['explore_count'] = p.get('explore_count', 0) + 1
    clover_gain = random.randint(1, 2)
    p['clovers'] += clover_gain
    save_player(uid, p)

    roll = random.random()
    # Chest Logic (using media IDs from media_assets.json)
    if roll < 0.005:
        # Frost Chest logic...
        await update.message.reply_photo(MEDIA["IMAGES"]["CHESTS"]["FROST"], caption="...")
        return
    # ... (Other chest logic follows same pattern)

    # Encounter Logic
    char_name = random.choice(list(DATA["EXPLORE_DATA"].keys()))
    img_id = DATA["EXPLORE_DATA"][char_name]
    text = f"🧭 **EXPLORATION** 🧭\n\nYou encountered **{char_name}** while sailing!"
    
    pending_explores[uid] = {'name': char_name, 'time': time.time()}
    kb = [[InlineKeyboardButton(f"Fight {char_name} ⚔", callback_data=f"efight_{char_name}")]]
    
    await update.message.reply_photo(img_id, caption=text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

def register(application):
    application.add_handler(CommandHandler("explore", explore_cmd))
