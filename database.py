import logging
from pymongo import MongoClient
from datetime import datetime
from config import Config

# Initialize MongoDB Client
try:
    mongo_client = MongoClient(Config.MONGO_URI)
    # Verify connection
    mongo_client.admin.command('ping')
    db = mongo_client["pirate_v3"]
    players_collection = db["players"]
    logging.info("✅ Connected to MongoDB Atlas successfully.")
except Exception as e:
    logging.error(f"❌ Failed to connect to MongoDB: {e}")
    players_collection = None

def save_player(user_id, player_data):
    """
    Saves or updates player data. 
    Handles nested character lists and equipment states.
    """
    if players_collection is None: 
        return
    try:
        player_data['user_id'] = str(user_id)
        # Remove MongoDB's internal _id to prevent ImmutableField errors during update
        if '_id' in player_data:
            del player_data['_id']
            
        players_collection.update_one(
            {"user_id": str(user_id)},
            {"$set": player_data},
            upsert=True
        )
    except Exception as e:
        logging.error(f"Error saving player {user_id}: {e}")

def load_player(user_id):
    """
    Retrieves player data from the database.
    Returns a dictionary or None if not found.
    """
    if players_collection is None: 
        return None
    try:
        data = players_collection.find_one({"user_id": str(user_id)})
        if data:
            if '_id' in data:
                del data['_id']
            return data
        return None
    except Exception as e:
        logging.error(f"Error loading player {user_id}: {e}")
        return None

def get_player(user_id, username=None):
    """
    Returns existing player data or initializes a new pirate profile with default stats.
    """
    uid = str(user_id)
    p = load_player(uid)
    
    if not p:
        # [span_1](start_span)Default starting template[span_1](end_span)
        p = {
            "user_id": uid,
            "name": username or "Pirate",
            "team": [],
            "characters": [],
            "berries": 10000,
            "clovers": 0,
            "bounty": 0,
            "exp": 0,
            "level": 1,
            "starter_summoned": False,
            "wins": 0,
            "losses": 0,
            "explore_wins": 0,
            "kill_count": 0,
            "fruits": [],
            "equipped_fruit": None,
            "tokens": 0,
            "weapons": [],
            "explore_count": 0,
            "start_date": datetime.now().strftime("%Y-%m-%d"),
            "referred_by": None,
            "referrals": 0
        }
    else:
        # [span_2](start_span)Ensure new fields exist for old player profiles[span_2](end_span)
        defaults = {
            "fruits": [],
            "equipped_fruit": None,
            "weapons": [],
            "tokens": 0,
            "bounty": 0,
            "explore_wins": 0
        }
        for k, v in defaults.items():
            if k not in p:
                p[k] = v
                
    # [span_3](start_span)Admin Overrides[span_3](end_span)
    if int(user_id) in Config.ADMIN_IDS:
        p["berries"] = max(p.get("berries", 0), 99999999)
        p["clovers"] = max(p.get("clovers", 0), 99999999)
        p["level"] = 100

    save_player(uid, p)
    return p
