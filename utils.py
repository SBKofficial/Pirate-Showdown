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

def get_stats_text(char_obj_or_name, player_fruit=None):
    if isinstance(char_obj_or_name, str):
        name = char_obj_or_name
        lvl = 1
        weapon = None
    else:
        name = char_obj_or_name['name']
        lvl = char_obj_or_name.get('level', 1)
        weapon = char_obj_or_name.get('equipped_weapon')

    c = DATA["CHARACTERS"].get(name)
    if not c: return "Character not found."

    stats = get_scaled_stats({"name": name, "level": lvl}, player_fruit)
    ult_name = c['ult']
    # Moves data would ideally be in JSON too, but keeping it logic-based for now
    text = (
        f"《Name》: {name}\n"
        f"《Rarity》: {c['rarity']}\n"
        f"《 Class》: {c['class']}\n"
        f"《Level》: {lvl}\n\n"
        f"      《STATS》\n"
        f"《HP: {stats['hp']}\n"
        f"《ATK: {stats['atk_min']}-{stats['atk_max']}\n"
        f"《SPE: {stats['spe']}\n"
        f"《 DEF: {stats['def']}\n\n"
        f"■ 《BASIC》: {c['moves'][0]}\n"
        f"● 《BASIC》: {c['moves'][1]}\n"
        f"♤《 ULTIMATE》: {ult_name}"
    )
    if weapon:
        text += f"\n⚔️ 《WEAPON》: {weapon}"
    return text

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

def generate_char_instance(name, level=1, player_fruit=None, equipped_weapon=None):
    c = DATA["CHARACTERS"].get(name)
    stats = get_scaled_stats({"name": name, "level": level}, player_fruit)
    return {
        "id": str(uuid.uuid4())[:8], "name": name, "level": level, "exp": 0,
        "hp": stats['hp'], "max_hp": stats['hp'], "atk_min": stats['atk_min'],
        "atk_max": stats['atk_max'], "def": stats['def'], "spe": stats['spe'],
        "moves": list(c['moves']), "ult": c['ult'], "stunned": False, "ult_used": False,
        "equipped_weapon": equipped_weapon
    }

def get_bar(h, m):
    if m <= 0: return "▒" * 10
    ratio = max(0, min(1, h/m))
    filled = int(ratio * 10)
    return "█" * filled + "▒" * (10 - filled)
