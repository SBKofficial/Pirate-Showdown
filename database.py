import logging
from pymongo import MongoClient
from config import Config

# Setup logging to see connection status in Stackhost logs
logger = logging.getLogger(__name__)

try:
    # Initialize client with a 5-second timeout
    mongo_client = MongoClient(Config.MONGO_URI, serverSelectionTimeoutMS=5000)
    # The 'ping' command forces a connection check immediately
    mongo_client.admin.command('ping')
    db = mongo_client["pirate_v3"]
    players_collection = db["players"]
    logger.info("✅ Connected to MongoDB Atlas successfully.")
except Exception as e:
    logger.error(f"❌ Failed to connect to MongoDB: {e}")
    players_collection = None

def load_player(user_id):
    if players_collection is None: return None
    return players_collection.find_one({"user_id": str(user_id)})

def save_player(user_id, data):
    if players_collection is None: return
    # Remove _id if it exists to prevent ImmutableField errors
    if '_id' in data: del data['_id']
    players_collection.update_one({"user_id": str(user_id)}, {"$set": data}, upsert=True)

def get_player(user_id, name="Pirate"):
    p = load_player(user_id)
    if not p:
        # Default starting template for new players
        p = {
            "user_id": str(user_id), 
            "name": name, 
            "level": 1, 
            "exp": 0, 
            "berries": 1000, 
            "clovers": 0, 
            "team": [], 
            "characters": []
        }
        save_player(user_id, p)
    return p
