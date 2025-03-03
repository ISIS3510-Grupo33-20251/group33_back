#File for connecting to the database
from motor.motor_asyncio import AsyncIOMotorClient

# MongoDB connection URI
MONGO_URI = "mongodb://localhost:27017/"

# Database name
DB_NAME = "universe_app"

# Create a new MongoDB client
client = AsyncIOMotorClient(MONGO_URI)
database = client[DB_NAME]