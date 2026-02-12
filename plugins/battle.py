import time
import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes
from database import get_player, save_player, load_player
from utils import DATA, MEDIA, get_bar, generate_char_instance, check_player_levelup, check_char_levelup

battles = {}

# =====================
# MOVE EFFECT LOGIC
# =====================
def apply_move_effects(attacker, defender, move_name, att_team):
    # This dictionary maps move names to their original code effects
    effects = {
        "Sube sube no mi": "def_buff_10",
        "Kokutei Roseo Metal": "team_heal_50",
        "Kiribachi": "atk_buff_15_2",
        "Honesty impact": "dodge_30",
        "Usopp hammer": "usopp_ult",
        "Bara Bara festival": "team_atk_5",
        "Firey morale": "helmeppo_ult",
        "Zeus breeze tempo": "stun_1",
        "Thunder Bagua": "yamato_ult",
        "Damned Punk": "kid_ult"
    }
    
    effect = effects.get(move_name)
    if not effect: return ""

    if effect == "def_buff_10": 
        attacker['def'] += 10
    elif effect == "team_heal_50":
        for char in att_team: char['hp'] = min(char['max_hp'], char['hp'] + 50)
    elif effect == "atk_buff_15_2":
        attacker['atk_min'] = int(attacker['atk_min'] * 1.15)
        attacker['atk_max'] = int(attacker['atk_max'] * 1.15)
    elif effect == "dodge_30": 
        attacker['dodge_chance'] = 30
    elif effect == "stun_1": 
        defender['stunned'] = True
    elif effect == "yamato_ult":
        attacker['dodge_chance'] = 50
        attacker['atk_min'] = int(attacker['atk_min'] * 1.1)
        attacker['def'] = int(attacker['def'] * 1.15)
    
    return f"\n✨ **{move_name}** effect activated!"

# =====================
# CORE BATTLE ENGINE
# =====================
async def run_battle_turn(query, battle_id, move_name=None, context=None):
    b = battles.get(battle_id)
    if not b: return

    b['last_move_time'] = time.time()
    p1_char = b['p1_team'][b['p1_idx']]
    p2_char = b['p2_team'][b['p2_idx']]

    if b['turn_owner'] == "p1":
        attacker, defender, att_p, def_p = p1_char, p2_char, "p1", "p2"
    else:
        attacker, defender, att_p, def_p = p2_char, p1_char, "p2", "p1"

    att_team = b[f'{att_p}_team']

    # Stun Check
    if attacker.get('stunned'):
        attacker['stunned'] = False
        await show_move_selection(query, battle_id, f"💫 **{attacker['name']}** is stunned and skips!", context)
        return

    # NPC AI
    if b.get('is_npc') and b['turn_owner'] == "p2":
        move_name = random.choice(attacker['moves'] + ([attacker['ult']] if not attacker.get('ult_used') else []))

    if not move_name:
        await show_move_selection(query, battle_id, context=context)
        return

    # Damage Calculation
    # (Base logic: Atk + MoveDmg - Def)
    move_dmg = 30 # Default if move not in data
    # (Simplified for demonstration, use DATA["MOVES"] in production)
    
    damage = max(5, (random.randint(attacker['atk_min'], attacker['atk_max']) + move_dmg + 120) - defender['def'])
    defender['hp'] -= damage
    log = f"🔥 **{attacker['name']}** hits with **{move_name}**!\n💥 Deals **{damage}** DMG!"
    
    # Apply Effects
    log += apply_move_effects(attacker, defender, move_name, att_team)

    if defender['hp'] <= 0:
        defender['hp'] = 0
        b[f'{def_p}_idx'] += 1
        log += f"\n💀 **{defender['name']}** has fallen!"

        if b[f'{def_p}_idx'] >= len(b[f'{def_p}_team']):
            await handle_battle_win(query, battle_id, att_p)
            return

    b['turn_owner'] = def_p
    await show_move_selection(query, battle_id, log, context)

async def handle_battle_win(query, battle_id, winner_p):
    b = battles.get(battle_id)
    winner_id = b[f'{winner_p}_id']
    p = get_player(winner_id)
    
    exp_gain = random.randint(100, 200)
    p['exp'] += exp_gain
    check_player_levelup(p)
    save_player(winner_id, p)
    
    await query.edit_message_text(f"🏆 **{b[winner_p + '_name']}** triumphed!\n🌟 Gained {exp_gain} EXP!")
    if battle_id in battles: del battles[battle_id]

async def show_move_selection(query, battle_id, log="", context=None):
    b = battles.get(battle_id)
    p1_char = b['p1_team'][b['p1_idx']]
    p2_char = b['p2_team'][b['p2_idx']]
    
    status = (
        f"⚔️ **ARENA** ⚔️\n"
        f"👤 {b['p1_name']}: {p1_char['hp']}/{p1_char['max_hp']}\n`{get_bar(p1_char['hp'], p1_char['max_hp'])}`\n"
        f"👤 {b['p2_name']}: {p2_char['hp']}/{p2_char['max_hp']}\n`{get_bar(p2_char['hp'], p2_char['max_hp'])}`\n"
        f"\n{log}\n⌛️ Turn: {b[b['turn_owner'] + '_name']}"
    )
    
    attacker = b[b['turn_owner'] + '_team'][b[b['turn_owner'] + '_idx']]
    kb = []
    for move in attacker['moves']:
        kb.append([InlineKeyboardButton(f"👊 {move}", callback_data=f"bmove|{battle_id}|{move}")])
    
    await query.edit_message_text(status, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

async def battle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        await run_battle_turn(query, bid, move_name=move, context=context)

def register(application):
    application.add_handler(CallbackQueryHandler(battle_callback, pattern="^(efight_|bmove|accept_)"))
