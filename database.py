import logging
from pymongo import MongoClient
from datetime import datetime
from config import Config

# Initialize Client
try:
    mongo_client = MongoClient(Config.MONGO_URI)
    db = mongo_client["pirate_v3"]
    players_collection = db["players"]
    logging.info("✅ Connected to MongoDB Atlas successfully.")
except Exception as e:
    logging.error(f"❌ Failed to connect to MongoDB: {e}")
    players_collection = None

def save_player(user_id, player_data):
    if players_collection is None: return
    player_data['user_id'] = str(user_id)
    if '_id' in player_data:
        del player_data['_id']
    players_collection.update_one(
        {"user_id": str(user_id)},
        {"$set": player_data},
        upsert=True
    )

def load_player(user_id):
    if players_collection is None: return None
    data = players_collection.find_one({"user_id": str(user_id)})
    if data and '_id' in data:
        del data['_id']
    return data
