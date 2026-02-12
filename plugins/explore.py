import random
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, ContextTypes
from database import get_player, save_player
from utils import MEDIA, DATA

# To prevent multiple concurrent explores in the same session
pending_explores = {}

async def explore_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the main exploration logic, chest finds, and encounters."""
    if update.effective_chat.type != "private":
        await update.message.reply_text("⚠️ Please use /explore in private messages to sail the Grand Line.")
        return

    uid = str(update.effective_user.id)
    p = get_player(uid)
    
    # Simple 2-minute cooldown check
    if uid in pending_explores:
        last_time = pending_explores[uid].get('time', 0)
        if time.time() - last_time < 120:
            remaining = int(120 - (time.time() - last_time))
            await update.message.reply_text(f"⚠️ Your crew is resting! New exploration available in {remaining}s.")
            return

    # Update player stats for exploring
    p['explore_count'] = p.get('explore_count', 0) + 1
    p['clovers'] = p.get('clovers', 0) + random.randint(1, 3)
    save_player(uid, p)

    roll = random.random()

    # --- CHEST LOGIC (Using your Media_assets.json structure) ---
    # Frost Chest (0.5% chance)
    if roll < 0.005:
        c_luck, c_berry, c_tokens = random.randint(15, 25), random.randint(4000, 6000), 5
        p['clovers'] += c_luck; p['berries'] += c_berry; p['tokens'] += c_tokens
        save_player(uid, p)
        img = MEDIA["IMAGES"]["CHESTS"]["FROST"]
        await update.message.reply_photo(img, caption=f"❄️ **FROST CHEST FOUND!**\n\nRewards:\n🍀 {c_luck} Clovers\n🍇 {c_berry} Berries\n🧩 {c_tokens} Tokens")
        return

    # Gold Chest (1.5% chance)
    elif roll < 0.02:
        c_luck, c_berry, c_tokens = random.randint(5, 12), random.randint(2000, 3500), 2
        p['clovers'] += c_luck; p['berries'] += c_berry; p['tokens'] += c_tokens
        save_player(uid, p)
        img = MEDIA["IMAGES"]["CHESTS"]["GOLD"]
        await update.message.reply_photo(img, caption=f"💰 **GOLDEN CHEST FOUND!**\n\nRewards:\n🍀 {c_luck} Clovers\n🍇 {c_berry} Berries\n🧩 {c_tokens} Tokens")
        return

    # --- ENCOUNTER LOGIC ---
    # Pick a random character from your CHARACTERS list in Game_data.json
    char_list = list(DATA["CHARACTERS"].keys())
    # Exclude Legendaries from common exploration encounters if desired
    common_enemies = [c for c in char_list if "Legendary" not in DATA["CHARACTERS"][c]["rarity"]]
    enemy_name = random.choice(common_enemies if common_enemies else char_list)
    
    # Record the encounter time
    pending_explores[uid] = {'name': enemy_name, 'time': time.time()}

    # Use the Default image if specific enemy images aren't in media_assets
    enemy_img = MEDIA["IMAGES"].get(enemy_name, MEDIA["IMAGES"]["Default"])
    
    text = (
        f"🧭 **EXPLORATION** 🧭\n\n"
        f"You encountered **{enemy_name}** while sailing!\n"
        f"Rarity: {DATA['CHARACTERS'][enemy_name]['rarity']}\n"
        f"Class: {DATA['CHARACTERS'][enemy_name]['class']}\n\n"
        f"Do you wish to engage in battle?"
    )
    
    kb = [[InlineKeyboardButton(f"Fight {enemy_name} ⚔️", callback_data=f"efight_{enemy_name}")]]
    await update.message.reply_photo(enemy_img, caption=text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

def register(application):
    application.add_handler(CommandHandler("explore", explore_cmd))
