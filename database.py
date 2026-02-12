import logging
import urllib.parse
from pymongo import MongoClient
from config import Config

# Setup logging
logger = logging.getLogger(__name__)

def get_db_connection():
    try:
        # 1. URL Encode the credentials to handle the '??' in your password
        # This prevents the "Port contains non-digit characters" error
        user = "Znxpirateshowdown"
        password = urllib.parse.quote_plus("1234Qwer??") 
        cluster = "znx.idxdehh.mongodb.net"
        app_name = "Znx"
        
        # 2. Construct the safe URI
        uri = f"mongodb+srv://{user}:{password}@{cluster}/?appName={app_name}"

        # 3. Initialize the client
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        
        # 4. Verify the connection
        client.admin.command('ping')
        logger.info("✅ Connected to MongoDB Atlas successfully.")
        return client["pirate_v3"]
    except Exception as e:
        logger.error(f"❌ Failed to connect to MongoDB: {e}")
        return None

# Global collection objects
db = get_db_connection()
players_collection = db["players"] if db is not None else None

def load_player(user_id):
    if players_collection is None: return None
    return players_collection.find_one({"user_id": str(user_id)})

def save_player(user_id, data):
    if players_collection is None: return
    if '_id' in data: del data['_id']
    players_collection.update_one({"user_id": str(user_id)}, {"$set": data}, upsert=True)

def get_player(user_id, name="Pirate"):
    p = load_player(user_id)
    if not p:
        p = {
            "user_id": str(user_id), "name": name, "level": 1, "exp": 0, 
            "berries": 1000, "clovers": 0, "team": [], "characters": []
        }
        save_player(user_id, p)
    return p
