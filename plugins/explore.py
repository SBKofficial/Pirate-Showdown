import random
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, ContextTypes, CallbackQueryHandler
from database import get_player, load_player, save_player
from utils import MEDIA, DATA

pending_explores = {}

async def explore_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        await update.message.reply_text("⚠️ Use this command in private messages (DM).")
        return

    uid = str(update.effective_user.id)
    p = get_player(uid)

    if uid in pending_explores:
        last_time = pending_explores[uid].get('time', 0)
        if time.time() - last_time < 120:
            remaining = int(120 - (time.time() - last_time))
            await update.message.reply_text(f"⚠️ Finish your battle! New explore in {remaining}s.")
            return
        del pending_explores[uid]

    p['explore_count'] = p.get('explore_count', 0) + 1
    p['clovers'] += random.randint(1, 2)
    save_player(uid, p)

    roll = random.random()
    if roll < 0.005:
        p['clovers'] += 20; p['berries'] += 5000; p['tokens'] += 5
        save_player(uid, p)
        await update.message.reply_photo(MEDIA["IMAGES"]["CHESTS"]["FROST"], caption="Found a Frost Chest! 🍀20, 🍇5000, 🧩5")
        return
    # Add Gold/Dark chest logic here as per original bot.py...

    char_name = random.choice(list(DATA["EXPLORE_DATA"].keys()))
    img_id = DATA["EXPLORE_DATA"][char_name]
    pending_explores[uid] = {'name': char_name, 'time': time.time()}

    kb = [[InlineKeyboardButton(f"Fight {char_name} ⚔", callback_data=f"efight_{char_name}")]]
    await update.message.reply_photo(img_id, caption=f"🧭 Encountered **{char_name}**!", reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

def register(application):
    application.add_handler(CommandHandler("explore", explore_cmd))
