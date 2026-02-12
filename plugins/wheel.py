import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaVideo
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes
from database import get_player, save_player
from utils import DATA, MEDIA, generate_char_instance

async def wheel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Triggers the main wheel selection menu."""
    desc = "🎡 **PIRATE WHEELS** 🎡\n\nChoose the wheel you want to spin!"
    kb = [
        [InlineKeyboardButton("Character Wheel 👤", callback_data="char_wheel")],
        [InlineKeyboardButton("Resource Wheel 💎", callback_data="res_wheel")]
    ]
    await update.message.reply_video(MEDIA["VIDEOS"]["WHEEL"], caption=desc, reply_markup=InlineKeyboardMarkup(kb))

async def wheel_options(query, type_name):
    """Shows the pull options (1x or 5x) for the selected wheel."""
    if type_name == "Character":
        cost1, cost5 = "150 🍀", "500 🍀"
        data_c1, data_c5 = "wheel_1_Character", "wheel_5_Character"
    else:
        cost1, cost5 = "100 🍀", "400 🍀"
        data_c1, data_c5 = "wheel_1_Resource", "wheel_5_Resource"

    desc = f"🎡 {type_name.upper()} WHEEL 🎡\n\n1x Pull: {cost1}\n5x Pull: {cost5}"
    kb = [
        [InlineKeyboardButton("1x Pull", callback_data=data_c1), 
         InlineKeyboardButton("5x Pull", callback_data=data_c5)],
        [InlineKeyboardButton("Back", callback_data="wheel_cancel"), 
         InlineKeyboardButton("Probability", callback_data="wheel_prob")]
    ]
    await query.edit_message_media(InputMediaVideo(MEDIA["VIDEOS"]["WHEEL"], caption=desc), reply_markup=InlineKeyboardMarkup(kb))

async def handle_wheel(query, p, count, wheel_type):
    """Processes the actual spin logic and rewards."""
    uid = str(p['user_id'])
    cost = 150 if count == 1 else 500 if wheel_type == "Character" else 100 if count == 1 else 400

    if p.get("clovers", 0) < cost:
        await query.answer("Not enough 🍀 Clovers!", show_alert=True)
        return

    p["clovers"] -= cost
    results = []
    special_anim = None

    if wheel_type == "Character":
        for _ in range(count):
            roll = random.random()
            if roll < 0.02:
                res = "Yamato"
                special_anim = MEDIA["VIDEOS"]["YAMATO_SUMMON"]
            elif roll < 0.04:
                res = "Eustass Kid"
                special_anim = MEDIA["VIDEOS"]["KID_SUMMON"]
            else:
                others = [c for c in DATA["CHARACTERS"].keys() if c not in ["Yamato", "Eustass Kid"]]
                res = random.choice(others)

            char_data = DATA["CHARACTERS"][res]
            rarity_prefix = "🟨 " if "Legendary" in char_data['rarity'] else "🟦 " if "Rare" in char_data['rarity'] else "⬜️ "

            existing = next((c for c in p["characters"] if c["name"] == res), None)
            if existing:
                existing["level"] = existing.get("level", 1) + 1
                results.append(f"{rarity_prefix}{res} (Lv.{existing['level']})")
            else:
                p["characters"].append(generate_char_instance(res))
                results.append(f"{rarity_prefix}{res} (New!)")
    else:
        for _ in range(count):
            roll = random.random()
            if roll < 0.05:
                fruit_name = random.choice(list(DATA["DEVIL_FRUITS"].keys()))
                p.setdefault("fruits", []).append(fruit_name)
                results.append(f"🍎 {fruit_name} (NEW!)")
            elif roll < 0.15:
                clovers = random.randint(10, 50)
                p['clovers'] += clovers
                results.append(f"🍀 {clovers} Clovers")
            else:
                berries = random.randint(5000, 15000)
                p['berries'] += berries
                results.append(f"🍇 {berries} Berries")

    save_player(uid, p)
    res_text = f"🎰 **{wheel_type.upper()} RESULTS**:\n\n" + "\n".join(results)
    final_anim = special_anim if special_anim else MEDIA["VIDEOS"]["SUMMON_ANIM"]
    
    await query.edit_message_media(InputMediaVideo(final_anim, caption=res_text), reply_markup=None)

async def wheel_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Routes callback data for the wheel system."""
    query = update.callback_query
    data = query.data
    p = get_player(query.from_user.id)

    if data == "char_wheel": await wheel_options(query, "Character")
    elif data == "res_wheel": await wheel_options(query, "Resource")
    elif data == "wheel_cancel": await query.message.delete()
    elif data == "wheel_prob":
        await query.answer("📊 PROBABILITIES\nYamato: 2%\nKid: 2%\nFruits: 5%\nOthers: Balanced", show_alert=True)
    elif data.startswith("wheel_"):
        parts = data.split("_")
        await handle_wheel(query, p, int(parts[1]), parts[2])

def register(application):
    application.add_handler(CommandHandler("wheel", wheel_cmd))
    application.add_handler(CallbackQueryHandler(wheel_callback_handler, pattern="^(char_wheel|res_wheel|wheel_.*)"))
