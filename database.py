import logging
from pymongo import MongoClient
from config import Config

try:
    # The client will now use the URI from Config (which you will update in Stackhost)
    mongo_client = MongoClient(Config.MONGO_URI, serverSelectionTimeoutMS=5000)
    # The ping command verifies the connection is actually alive
    mongo_client.admin.command('ping')
    db = mongo_client["pirate_v3"]
    players_collection = db["players"]
    logging.info("✅ Connected to MongoDB Atlas successfully.")
except Exception as e:
    logging.error(f"❌ Failed to connect to MongoDB: {e}")
    players_collection = None

def load_player(user_id):
    if players_collection is None: return None
    return players_collection.find_one({"user_id": str(user_id)})

def save_player(user_id, data):
    if players_collection is None: return
    players_collection.update_one({"user_id": str(user_id)}, {"$set": data}, upsert=True)

def get_player(user_id, name="Pirate"):
    p = load_player(user_id)
    if not p:
        p = {"user_id": str(user_id), "name": name, "level": 1, "exp": 0, "berries": 1000, "clovers": 0, "team": [], "characters": []}
        save_player(user_id, p)
    return p
