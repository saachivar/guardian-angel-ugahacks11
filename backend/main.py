
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Header, Depends
from fastapi.responses import FileResponse
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import os



# MongoDB setup
MONGO_URI = "mongodb+srv://db_user:db_pass@guardian-angel.k4xhwty.mongodb.net/"
client = MongoClient(MONGO_URI)
db = client["guardian_angel"]
events_collection = db["events"]

app = FastAPI(title="Guardian Angel Backend")

def serialize_event(doc):
    return {
        "id": str(doc["_id"]),
        "timestamp": doc.get("timestamp"),
        "confidence": doc.get("confidence"),
        "clip_path": doc.get("clip_path"),
        "device_id": doc.get("device_id"),
        "resolved": doc.get("resolved", 0)
    }

# ------------------------------
# Upload video + metadata
# ------------------------------
@app.post("/upload")
async def upload_event(
    device_id: str = Form(...),
    confidence: float = Form(...),
    timestamp: str = Form(None),
    file: UploadFile = File(... )
):
    # Ensure clips folder exists
    os.makedirs("clips", exist_ok=True)

    # Use current time if no timestamp provided
    if not timestamp:
        timestamp = datetime.now().isoformat()

    # Save file
    filename = f"{device_id}_{timestamp.replace(':','_')}_{file.filename}"
    path = os.path.join("clips", filename)
    with open(path, "wb") as f:
        f.write(await file.read())

    # Create event document
    event = {
        "timestamp": timestamp,
        "confidence": confidence,
        "clip_path": path,
        "device_id": device_id,
        "resolved": 0
    }

    result = events_collection.insert_one(event)
    return {
        "status": "success",
        "id": str(result.inserted_id),
        "event": serialize_event(event)
    }
    
    # Fetch the inserted doc to return it nicely
    saved_event = events_collection.find_one({"_id": result.inserted_id})

    return {
        "status": "success",
        "id": str(result.inserted_id),
        "event": serialize_event(saved_event)
    }

