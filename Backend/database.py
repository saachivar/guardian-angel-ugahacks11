from pymongo import MongoClient
from datetime import datetime

# ------------------------------
# 1️⃣ Connect to MongoDB Atlas
# ------------------------------
# Replace with your credentials
MONGO_URI = "mongodb+srv://db_user:db_pass@guardian-angel.k4xhwty.mongodb.net/"
client = MongoClient(MONGO_URI)

# Access your database
db = client["guardian_angel"]  # Will be created if it doesn't exist

# Access your collection
events_collection = db["events"]  # Will be created if it doesn't exist

# ------------------------------
# 2️⃣ Helper function to insert an event
# ------------------------------
def insert_event(timestamp=None, confidence=1.0, clip_path="", device_id="pi01"):
    """
    Insert a new fall event into MongoDB.
    timestamp: ISO string or None → defaults to now
    confidence: float
    clip_path: path to MP4 file
    device_id: identifier for the Pi / device
    """
    if timestamp is None:
        timestamp = datetime.now().isoformat()
    
    event = {
        "timestamp": timestamp,
        "confidence": confidence,
        "clip_path": clip_path,
        "device_id": device_id,
        "resolved": 0  # 0=active, 1=resolved, 2=false alarm
    }
    
    result = events_collection.insert_one(event)
    print(f"Inserted event with ID: {result.inserted_id}")
    return result.inserted_id

# ------------------------------
# 3️⃣ Example usage
# ------------------------------
if __name__ == "__main__":
    # Test insert
    insert_event(confidence=0.95, clip_path="clips/fall_test.mp4", device_id="pi01")
