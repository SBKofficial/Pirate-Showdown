import json
import random
import uuid
import logging
from datetime import datetime
from database import load_player, save_player, Config

# Load JSON Data
def load_game_data():
    with open('data/game_data.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def load_media_assets():
    with open('data/media_assets.json', 'r', encoding='utf-8') as f:
        return json.load(f)

DATA = load_game_data()
MEDIA = load_media_assets()

# LEVELING UTILS
def get_required_char_exp(level):
    if 1 <= level <= 5: return 500
    if 6 <= level <= 10: return 1000
    if 11 <= level <= 15: return 2000
    if 16 <= level <= 20: return 2500
    return 3000

def get_required_player_exp(level):
    if level >= 100: return 999999999
    if 1 <= level <= 5: return 200
    if 6 <= level <= 10: return 500
    if 11 <= level <= 20: return 1500
    if 21 <= level <= 30: return 2000
    if 31 <= level <= 70: return 3000
    if 71 <= level <= 100: return 6000
    return 10000

def check_player_levelup(p):
    lvl = p.get('level', 1)
    exp = p.get('exp', 0)
    req = get_required_player_exp(lvl)
    levels_gained = 0
    while exp >= req and lvl < 100:
        exp -= req
        lvl += 1
        levels_gained += 1
        req = get_required_player_exp(lvl)
        p['clovers'] = p.get('clovers', 0) + 10
        p['berries'] = p.get('berries', 0) + 500
        p['bounty'] = p.get('bounty', 0) + 40
    p['level'] = lvl
    p['exp'] = exp
    return levels_gained

def check_char_levelup(char):
    lvl = char.get('level', 1)
    exp = char.get('exp', 0)
    req = get_required_char_exp(lvl)
    while exp >= req:
        exp -= req
        lvl += 1
        req = get_required_char_exp(lvl)
    char['level'] = lvl
    char['exp'] = exp

def get_scaled_stats(char_obj, player_fruit=None):
    name = char_obj['name']
    base = DATA["CHARACTERS"].get(name, DATA["CHARACTERS"]["Usopp"])
    lvl = char_obj.get('level', 1)
    bonus_multiplier = lvl - 1
    stats = {
        "hp": base['hp'] + (15 * bonus_multiplier),
        "atk_min": base['atk_min'] + (10 * bonus_multiplier),
        "atk_max": base['atk_max'] + (10 * bonus_multiplier),
        "def": base['def'] + (8 * bonus_multiplier),
        "spe": base['spe'] + (12 * bonus_multiplier)
    }
    if player_fruit and player_fruit in DATA["DEVIL_FRUITS"]:
        fruit = DATA["DEVIL_FRUITS"][player_fruit]
        stats['atk_min'] += fruit.get('atk_buff', 0)
        stats['atk_max'] += fruit.get('atk_buff', 0)
        stats['def'] += fruit.get('def_buff', 0)
        stats['hp'] += fruit.get('hp_buff', 0)
    return stats

def get_stats_text(char_obj_or_name, player_fruit=None):
    if isinstance(char_obj_or_name, str):
        name, lvl, weapon = char_obj_or_name, 1, None
    else:
        name, lvl, weapon = char_obj_or_name['name'], char_obj_or_name.get('level', 1), char_obj_or_name.get('equipped_weapon')
    
    c = DATA["CHARACTERS"].get(name)
    stats = get_scaled_stats({"name": name, "level": lvl}, player_fruit)
    
    text = (
        f"《Name》: {name}\n《Rarity》: {c['rarity']}\n《 Class》: {c['class']}\n"
        f"《Level》: {lvl}\n\n      《STATS》\n《HP: {stats['hp']}\n"
        f"《ATK: {stats['atk_min']}-{stats['atk_max']}\n《SPE: {stats['spe']}\n"
        f"《 DEF: {stats['def']}\n\n■ 《BASIC》: {c['moves'][0]}\n"
        f"● 《BASIC》: {c['moves'][1]}\n♤《 ULTIMATE》: {c['ult']}"
    )
    if weapon: text += f"\n⚔️ 《WEAPON》: {weapon}"
    return text

def generate_char_instance(name, level=1, player_fruit=None, equipped_weapon=None):
    stats = get_scaled_stats({"name": name, "level": level}, player_fruit)
    c = DATA["CHARACTERS"].get(name)
    return {
        "id": str(uuid.uuid4())[:8], "name": name, "level": level, "exp": 0,
        "hp": stats['hp'], "max_hp": stats['hp'], "atk_min": stats['atk_min'],
        "atk_max": stats['atk_max'], "def": stats['def'], "spe": stats['spe'],
        "moves": list(c['moves']), "ult": c['ult'], "stunned": False, "ult_used": False,
        "equipped_weapon": equipped_weapon, "dodge_chance": 0
    }

def get_bar(h, m):
    if m <= 0: return "▒" * 10
    ratio = max(0, min(1, h/m))
    filled = int(ratio * 10)
    return "█" * filled + "▒" * (10 - filled)
