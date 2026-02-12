import json
import random
import uuid
from datetime import datetime

# Helper to load JSON data
def load_game_data():
    with open('data/game_data.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def load_media_assets():
    with open('data/media_assets.json', 'r', encoding='utf-8') as f:
        return json.load(f)

DATA = load_game_data()
MEDIA = load_media_assets()

# [span_0](start_span)LEVELING MATH[span_0](end_span)
def get_required_player_exp(level):
    if level >= 100: return 999999999
    if 1 <= level <= 5: return 200
    if 6 <= level <= 10: return 500
    if 11 <= level <= 20: return 1500
    if 21 <= level <= 30: return 2000
    if 31 <= level <= 70: return 3000
    if 71 <= level <= 100: return 6000
    return 10000

# [span_1](start_span)STAT SCALING[span_1](end_span)
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
        stats['atk_min'] += fruit['atk_buff']
        stats['atk_max'] += fruit['atk_buff']
        stats['def'] += fruit['def_buff']
        stats['hp'] += fruit['hp_buff']
    return stats

def get_bar(h, m):
    if m <= 0: return "▒" * 10
    ratio = max(0, min(1, h/m))
    filled = int(ratio * 10)
    return "█" * filled + "▒" * (10 - filled)
