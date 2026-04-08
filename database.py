from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGODB_URI

# Connect to MongoDB
client = AsyncIOMotorClient(MONGODB_URI)
db = client['pokemon_bot']
users_collection = db['users']
pokemon_collection = db['pokemon_index'] # For the auto-scraper data

async def create_new_user(user_id: int):
    """Creates a fresh profile for a new player."""
    user_data = {
        "_id": user_id,  # Using Telegram ID as the unique document ID
        "coins": 500,
        "is_gym_leader": False,
        "gym_name": None,
        "gym_badge_file_id": None,
        "gym_losses": 0,
        "inventory": {
            "pokeball": 5,
            "great_ball": 0,
            "ultra_ball": 0,
            "master_ball": 0,
            "potion": 3
        },
        "party": [], # Max 6 Pokemon. Stored as dictionaries.
        "pc_box": [], # Infinite storage for caught Pokemon.
        "last_active": None
    }
    await users_collection.insert_one(user_data)

async def get_user(user_id: int):
    return await users_collection.find_one({"_id": user_id})

async def give_item(user_id: int, item: str, amount: int):
    """Admin tool to increment items."""
    await users_collection.update_one(
        {"_id": user_id},
        {"$inc": {f"inventory.{item}": amount}}
    )

async def set_gym_leader(user_id: int, status: bool):
    """Admin tool to force gym leader status."""
    await users_collection.update_one(
        {"_id": user_id},
        {"$set": {"is_gym_leader": status}}
    )
