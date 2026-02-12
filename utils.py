import json
import uuid
import logging
import random

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
def get_required_player_exp(level):
    if level >= 100: return 999999999
    if level <= 5: return 200
    if level <= 10: return 500
    if level <= 20: return 1500
    return 3000

def check_player_levelup(p):
    lvl = p.get('level', 1)
    exp = p.get('exp', 0)
    req = get_required_player_exp(lvl)
    gained = 0
    while exp >= req and lvl < 100:
        exp -= req
        lvl += 1
        gained += 1
        req = get_required_player_exp(lvl)
    p['level'], p['exp'] = lvl, exp
    return gained

# STATS & TEXT GENERATION
def get_scaled_stats(char_name, level=1):
    base = DATA["CHARACTERS"].get(char_name, DATA["CHARACTERS"]["Usopp"])
    mult = level - 1
    return {
        "hp": base['hp'] + (20 * mult),
        "atk_min": base['atk_min'] + (10 * mult),
        "atk_max": base['atk_max'] + (10 * mult),
        "def": base['def'] + (8 * mult),
        "spe": base['spe'] + (10 * mult)
    }

def get_stats_text(char_name):
    """Generates the stat string for the starter menu."""
    c = DATA["CHARACTERS"].get(char_name)
    stats = get_scaled_stats(char_name, 1)
    return (
        f"《Name》: {char_name}\n"
        f"《Rarity》: {c['rarity']}\n"
        f"《Class》: {c['class']}\n"
        f"《Level》: 1\n\n"
        f"      《STATS》\n"
        f"《HP: {stats['hp']}\n"
        f"《ATK: {stats['atk_min']}-{stats['atk_max']}\n"
        f"《DEF: {stats['def']}\n"
        f"《SPE: {stats['spe']}\n\n"
        f"■ 《BASIC》: {c['moves'][0]}\n"
        f"● 《BASIC》: {c['moves'][1]}\n"
        f"♤ 《ULTIMATE》: {c['ult']}"
    )

def generate_char_instance(name, level=1):
    stats = get_scaled_stats(name, level)
    c = DATA["CHARACTERS"][name]
    return {
        "id": str(uuid.uuid4())[:8], "name": name, "level": level, "exp": 0,
        "hp": stats['hp'], "max_hp": stats['hp'], "atk_min": stats['atk_min'],
        "atk_max": stats['atk_max'], "def": stats['def'], "moves": list(c['moves']),
        "ult": c['ult']
    }

def get_bar(h, m):
    ratio = max(0, min(1, h/m))
    filled = int(ratio * 10)
    return "█" * filled + "▒" * (10 - filled)
