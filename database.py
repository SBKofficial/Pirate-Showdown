import logging
import urllib.parse
from pymongo import MongoClient

# DNS fix for Termux
try:
    import dns.resolver
    dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
    dns.resolver.default_resolver.nameservers = ['8.8.8.8']
except ImportError:
    pass

logger = logging.getLogger(__name__)

def get_db_connection():
    try:
        user = "Znxpirateshowdown"
        # Auto-encoding '??' to '%3F%3F' for Stackhost compatibility
        password = urllib.parse.quote_plus("1234Qwer??") 
        cluster = "znx.idxdehh.mongodb.net"
        app_name = "Znx"
        
        uri = f"mongodb+srv://{user}:{password}@{cluster}/?appName={app_name}"
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        logger.info("✅ Connected to MongoDB Atlas successfully.")
        return client["pirate_v3"]
    except Exception as e:
        logger.error(f"❌ Failed to connect to MongoDB: {e}")
        return None

db_instance = get_db_connection()
players_collection = db_instance["players"] if db_instance is not None else None

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
            "berries": 1000, "clovers": 0, "team": [], "characters": [],
            "starter_summoned": False, "missions_completed": 0
        }
        save_player(user_id, p)
    return p
