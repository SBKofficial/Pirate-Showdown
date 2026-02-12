import json
import uuid
import random

def load_game_data():
    with open('data/game_data.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def load_media_assets():
    with open('data/media_assets.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# Global variables for all plugins to use
DATA = load_game_data()
MEDIA = load_media_assets()

def get_stats_text(char_name):
    """Pulls text and stats from game_data.json"""
    c = DATA["CHARACTERS"][char_name]
    # In a real scenario, you'd use your scaling logic here
    return (f"👤 **{char_name}**\n🎗 Rarity: {c['rarity']}\n⚔️ Class: {c['class']}\n"
            f"❤️ HP: {c['hp']}\n💥 Ult: {c['ult']}\n\n"
            f"📜 _Effect: {DATA['EFFECT_DESCRIPTIONS'].get(char_name, 'No info')}_")

def generate_char_instance(name, level=1):
    """Creates a character object using stats from game_data.json"""
    c = DATA["CHARACTERS"][name]
    return {
        "id": str(uuid.uuid4())[:8],
        "name": name,
        "level": level,
        "hp": c['hp'],
        "max_hp": c['hp'],
        "moves": list(c['moves']),
        "ult": c['ult']
    }
