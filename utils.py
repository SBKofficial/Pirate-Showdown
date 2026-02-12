import json
import uuid
import logging

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
    """Returns EXP needed for next player level."""
    if level >= 100: return 999999999
    levels = {5: 200, 10: 500, 20: 1500, 30: 2000, 70: 3000, 100: 6000}
    for threshold, exp in levels.items():
        if level <= threshold: return exp
    return 10000

def check_player_levelup(p):
    """Calculates level ups and rewards."""
    lvl, exp = p.get('level', 1), p.get('exp', 0)
    req = get_required_player_exp(lvl)
    gained = 0
    while exp >= req and lvl < 100:
        exp -= req
        lvl += 1
        gained += 1
        p['clovers'] = p.get('clovers', 0) + 10
        p['berries'] = p.get('berries', 0) + 500
        req = get_required_player_exp(lvl)
    p['level'], p['exp'] = lvl, exp
    return gained

def get_scaled_stats(char_obj, player_fruit=None):
    """Scales base stats from Game_data.json based on level."""
    name = char_obj['name']
    base = DATA["CHARACTERS"].get(name, DATA["CHARACTERS"]["Usopp"])
    lvl = char_obj.get('level', 1)
    mult = lvl - 1
    stats = {
        "hp": base['hp'] + (20 * mult),
        "atk_min": base['atk_min'] + (12 * mult),
        "atk_max": base['atk_max'] + (12 * mult),
        "def": base['def'] + (10 * mult),
        "spe": base['spe'] + (10 * mult)
    }
    # Apply Devil Fruit Buffs if equipped
    if player_fruit and player_fruit in DATA["DEVIL_FRUITS"]:
        f = DATA["DEVIL_FRUITS"][player_fruit]
        stats['atk_min'] += f.get('atk_buff', 0)
        stats['atk_max'] += f.get('atk_buff', 0)
        stats['def'] += f.get('def_buff', 0)
        stats['hp'] += f.get('hp_buff', 0)
    return stats

def get_bar(h, m):
    """Generates health bar UI."""
    ratio = max(0, min(1, h/m))
    filled = int(ratio * 10)
    return "█" * filled + "▒" * (10 - filled)

def generate_char_instance(name, level=1):
    """Creates a combat-ready character object."""
    stats = get_scaled_stats({"name": name, "level": level})
    c = DATA["CHARACTERS"][name]
    return {
        "id": str(uuid.uuid4())[:8], "name": name, "level": level,
        "hp": stats['hp'], "max_hp": stats['hp'],
        "atk_min": stats['atk_min'], "atk_max": stats['atk_max'],
        "def": stats['def'], "moves": list(c['moves']), "ult": c['ult']
    }
