import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    MONGO_URI = os.getenv("MONGO_URI")
    [span_1](start_span)ADMIN_IDS = [5242138546]  # From your original bot.py[span_1](end_span)
