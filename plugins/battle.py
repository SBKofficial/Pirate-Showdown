import time
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaVideo
from telegram.ext import CallbackQueryHandler, ContextTypes
from database import get_player, save_player
from utils import DATA, MEDIA, get_bar, generate_char_instance, check_player_levelup

battles = {}

async def run_battle_turn(query, bid, move_name=None):
    b = battles.get(bid)
    if not b: return

    # Character logic
    p1_char = b['p1_team'][b['p1_idx']]
    p2_char = b['p2_team'][b['p2_idx']]
    
    attacker, defender = (p1_char, p2_char) if b['turn'] == "p1" else (p2_char, p1_char)

    if move_name:
        # [span_14](start_span)Damage Math[span_14](end_span)
        dmg = max(10, random.randint(attacker['atk_min'], attacker['atk_max']) + 50 - defender['def'])
        defender['hp'] -= dmg
        log = f"⚔️ **{attacker['name']}** used {move_name}!\n💥 Deals {dmg} DMG!"
        
        if defender['hp'] <= 0:
            defender['hp'] = 0
            await query.edit_message_text(f"🏆 **{attacker['name']}** wins the battle!")
            del battles[bid]
            return
        
        b['turn'] = "p2" if b['turn'] == "p1" else "p1"

    # [span_15](start_span)UI Update[span_15](end_span)
    kb = [[InlineKeyboardButton(m, callback_data=f"bmove|{bid}|{m}")] for m in attacker['moves']]
    # [span_16](start_span)Add Ultimate button if available[span_16](end_span)
    kb.append([InlineKeyboardButton(f"🌟 {attacker['ult']}", callback_data=f"bmove|{bid}|{attacker['ult']}")])
    
    text = (f"👤 **{p1_char['name']}** vs 👤 **{p2_char['name']}**\n\n"
            f"HP: {p1_char['hp']}/{p1_char['max_hp']} `{get_bar(p1_char['hp'], p1_char['max_hp'])}`\n"
            f"HP: {p2_char['hp']}/{p2_char['max_hp']} `{get_bar(p2_char['hp'], p2_char['max_hp'])}`\n\n"
            f"It's **{b[b['turn'] + '_name']}**'s turn!")
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

async def battle_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    if data.startswith("efight_"):
        npc = data.split("_")[1]
        uid = str(query.from_user.id)
        p = get_player(uid)
        bid = f"bat_{uid}"
        battles[bid] = {
            "p1_id": uid, "p1_name": p['name'], "p1_team": [generate_char_instance("Usopp")], 
            "p2_name": npc, "p2_team": [generate_char_instance(npc)],
            "p1_idx": 0, "p2_idx": 0, "turn": "p1"
        }
        await run_battle_turn(query, bid)

    elif data.startswith("bmove|"):
        _, bid, move = data.split("|")
        await run_battle_turn(query, bid, move)

def register(application):
    application.add_handler(CallbackQueryHandler(battle_handler, pattern="^(efight_|bmove|accept_)"))
