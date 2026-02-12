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
    
    # 2-minute cooldown logic
    if uid in pending_explores:
        last_time = pending_explores[uid].get('time', 0)
        if time.time() - last_time < 120:
            remaining = int(120 - (time.time() - last_time))
            await update.message.reply_text(f"⚠️ You have an unfinished battle! Explore again in {remaining}s.")
            return

    p['explore_count'] = p.get('explore_count', 0) + 1
    p['clovers'] += random.randint(1, 2)
    save_player(uid, p)

    roll = random.random()
    # [span_2](start_span)Chest Rewards logic from original[span_2](end_span)
    if roll < 0.005:
        c_luck, c_berry, c_tokens = random.randint(15, 25), random.randint(4000, 6000), random.randint(4, 5)
        p['clovers'] += c_luck; p['berries'] += c_berry; p['tokens'] += c_tokens
        save_player(uid, p)
        await update.message.reply_photo(MEDIA["IMAGES"]["CHESTS"]["FROST"], 
            caption=f"While exploring, You found a Frost Chest\n\nIt contains\n{c_luck} 🍀\n{c_berry} 🍇\n{c_tokens} Level up token🧩")
        return
    elif roll < 0.015:
        c_luck, c_berry, c_tokens = random.randint(5, 10), random.randint(2000, 4000), random.randint(1, 2)
        p['clovers'] += c_luck; p['berries'] += c_berry; p['tokens'] += c_tokens
        save_player(uid, p)
        await update.message.reply_photo(MEDIA["IMAGES"]["CHESTS"]["GOLD"], 
            caption=f"While exploring, You found a Golden Chest\n\nIt contains\n{c_luck} 🍀\n{c_berry} 🍇\n{c_tokens} Level up token🧩")
        return

    # Encounter Logic (Bosses vs Regular NPCs)
    wins = p.get('explore_wins', 0)
    # [span_3](start_span)Mapping wins to Boss Missions from BOSS_MISSIONS[span_3](end_span)
    boss_mission = DATA["BOSS_MISSIONS"].get(str(wins))
    
    if boss_mission:
        char_name = boss_mission['name']
        img_id = boss_mission['img']
        text = f"🚨 **MISSION BOSS ENCOUNTER** 🚨\n\nYou've defeated {wins} challengers! The boss **{char_name}** has appeared!"
    else:
        char_name = random.choice(list(DATA["EXPLORE_DATA"].keys()))
        img_id = DATA["EXPLORE_DATA"][char_name]
        text = f"🧭 **EXPLORATION** 🧭\n\nYou encountered **{char_name}** while sailing!"

    pending_explores[uid] = {'name': char_name, 'time': time.time()}
    kb = [[InlineKeyboardButton(f"Fight {char_name} ⚔", callback_data=f"efight_{char_name}")]]
    await update.message.reply_photo(img_id, caption=text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

def register(application):
    application.add_handler(CommandHandler("explore", explore_cmd))
