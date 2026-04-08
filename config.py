import os
from dotenv import load_dotenv

# Load local .env file if running on PC, ignores if on Render
load_dotenv() 

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
API_ID = os.environ.get("API_ID", "")
API_HASH = os.environ.get("API_HASH", "")
MONGODB_URI = os.environ.get("MONGODB_URI", "")

# Convert space-separated string of IDs into a list of integers for God Mode
ADMINS = [int(x) for x in os.environ.get("ADMINS", "").split()]

LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", 0))
DUMP_CHANNEL = int(os.environ.get("DUMP_CHANNEL", 0))

# Render assigns a dynamic port, default to 8080 locally
PORT = int(os.environ.get("PORT", 8080))
