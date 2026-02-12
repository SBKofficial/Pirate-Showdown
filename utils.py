import json
import uuid
import random

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

# Global data access
DATA = load_json('data/game_data.json')
MEDIA = load_json('data/media_assets.json')

def get_stats_text(char_name):
    """Generates the detailed UI text for a character."""
    c = DATA["CHARACTERS"].get(char_name)
    if not c: return "Character not found."
    
    # Text UI details provided by user
    effect = DATA["EFFECT_DESCRIPTIONS"].get(char_name, "No description available.")
    
    return (
        f"👤 **{char_name}**\n"
        f"🎗 Rarity: {c['rarity']}\n"
        f"⚔️ Class: {c['class']}\n\n"
        f"❤️ HP: {c['hp']}\n"
        f"⚔️ ATK: {c['atk_min']}-{c['atk_max']}\n"
        f"🛡 DEF: {c['def']}\n"
        f"⚡️ SPE: {c['spe']}\n\n"
        f"💥 **ULT: {c['ult']}**\n"
        f"📜 _Effect: {effect}_"
    )

def generate_char_instance(name, level=1):
    c = DATA["CHARACTERS"][name]
    return {
        "id": str(uuid.uuid4())[:8],
        "name": name,
        "level": level,
        "hp": c['hp'],
        "max_hp": c['hp'],
        "atk_min": c['atk_min'],
        "atk_max": c['atk_max'],
        "def": c['def'],
        "moves": list(c['moves']),
        "ult": c['ult']
    }
