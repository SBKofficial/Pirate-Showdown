import time
import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes
from database import get_player, save_player, load_player
from utils import DATA, MEDIA, get_bar, generate_char_instance, check_player_levelup, check_char_levelup

battles = {}

async def run_battle_turn(query, battle_id, move_name=None, context=None):
    b = battles.get(battle_id)
    if not b: return

    b['last_move_time'] = time.time()
    p1_char = b['p1_team'][b['p1_idx']]
    p2_char = b['p2_team'][b['p2_idx']]

    attacker, defender, att_p, def_p = (p1_char, p2_char, "p1", "p2") if b['turn_owner'] == "p1" else (p2_char, p1_char, "p2", "p1")
    att_team = b[f'{att_p}_team']

    if attacker.get('stunned'):
        attacker['stunned'] = False
        await show_move_selection(query, battle_id, f"💫 **{attacker['name']}** is stunned!", context)
        return

    # NPC AI logic
    if b.get('is_npc') and b['turn_owner'] == "p2":
        move_name = random.choice(attacker['moves'] + ([attacker['ult']] if not attacker.get('ult_used') else []))

    if not move_name:
        await show_move_selection(query, battle_id, context=context)
        return

    # [span_1](start_span)Damage Calculation[span_1](end_span)
    move_data = DATA["MOVES"].get(move_name, {"dmg": 30})
    damage = max(5, (random.randint(attacker['atk_min'], attacker['atk_max']) + move_data['dmg'] + 120) - defender['def'])
    defender['hp'] -= damage
    log = f"🔥 **{attacker['name']}** used **{move_name}**!\n💥 Deals **{damage}** DMG!"

    if defender['hp'] <= 0:
        defender['hp'] = 0
        b[f'{def_p}_idx'] += 1
        if b[f'{def_p}_idx'] >= len(b[f'{def_p}_team']):
            await handle_battle_win(query, battle_id, att_p)
            return

    b['turn_owner'] = def_p
    await show_move_selection(query, battle_id, log, context)

async def handle_battle_win(query, battle_id, winner_p):
    b = battles.get(battle_id)
    winner_id = b[f'{winner_p}_id']
    p = get_player(winner_id)
    
    # [span_2](start_span)Reward logic[span_2](end_span)
    exp_gain = random.randint(50, 100)
    berry_gain = random.randint(50, 100)
    p['exp'] += exp_gain
    p['berries'] += berry_gain
    
    lvls = check_player_levelup(p)
    save_player(winner_id, p)
    
    result_text = f"🏆 **{b[winner_p + '_name']}** wins!\n🌟 +{exp_gain} EXP\n🍇 +{berry_gain} Berries"
    if lvls > 0: result_text += f"\n✨ Rank Up! Level {p['level']}"
    
    await query.edit_message_text(result_text)
    del battles[battle_id]

async def battle_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    uid = str(query.from_user.id)

    if data.startswith("efight_"):
        npc_name = data.split("_", 1)[1]
        p = get_player(uid)
        bid = f"explore_{uid}"
        battles[bid] = {
            "p1_id": uid, "p2_id": "NPC",
            "p1_team": [generate_char_instance(c['name'], c['level']) for c in p['team']],
            "p2_team": [generate_char_instance(npc_name)],
            "p1_name": p['name'], "p2_name": npc_name,
            "p1_idx": 0, "p2_idx": 0, "turn_owner": "p1", "is_npc": True,
            "last_move_time": time.time()
        }
        await run_battle_turn(query, bid, context=context)

    elif data.startswith("bmove|"):
        _, bid, move = data.split("|")
        b = battles.get(bid)
        if b and str(query.from_user.id) == (str(b['p1_id']) if b['turn_owner'] == "p1" else str(b['p2_id'])):
            await run_battle_turn(query, bid, move_name=move, context=context)

def register(application):
    application.add_handler(CommandHandler("battle", battle_request))
    application.add_handler(CallbackQueryHandler(battle_callback_handler, pattern="^(accept_|bmove|efight_|brun_|bforfeit_)"))
