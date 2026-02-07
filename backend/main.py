# main.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import os

# ------------------------------
# 1️⃣ MongoDB Setup
# ------------------------------
MONGO_URI = "mongodb+srv://db_user:db_pass@guardian-angel.k4xhwty.mongodb.net/"
client = MongoClient(MONGO_URI)
db = client["guardian_angel"]
events_collection = db["events"]

# ------------------------------
# 2️⃣ FastAPI Setup
# ------------------------------
app = FastAPI(title="Guardian Angel Backend")

# ------------------------------
# 3️⃣ Helper function
# ------------------------------
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
# 4️⃣ API Endpoints
# ------------------------------

# Create a new fall event
@app.post("/events")
def create_event(event: dict):
    """
    Expects JSON like:
    {
        "timestamp": "2026-02-07T12:00:00",  # optional
        "confidence": 0.95,
        "clip_path": "clips/fall1.mp4",
        "device_id": "pi01"
    }
    """
    if "timestamp" not in event or not event["timestamp"]:
        event["timestamp"] = datetime.now().isoformat()

    event["resolved"] = 0

    result = events_collection.insert_one(event)

    # ✅ Return JSON-safe response (NO ObjectId)
    return {
        "status": "success",
        "id": str(result.inserted_id),
        "event": {
            "timestamp": event["timestamp"],
            "confidence": event["confidence"],
            "clip_path": event["clip_path"],
            "device_id": event["device_id"],
            "resolved": event["resolved"]
        }
    }

# List all events
@app.get("/events")
def list_events():
    docs = events_collection.find().sort("_id", -1)
    return [serialize_event(d) for d in docs]

# Get a single event by ID
@app.get("/events/{event_id}")
def get_event(event_id: str):
    try:
        doc = events_collection.find_one({"_id": ObjectId(event_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    if not doc:
        raise HTTPException(status_code=404, detail="Event not found")

    return serialize_event(doc)

# Serve video clips
@app.get("/clips/{filename}")
def get_clip(filename: str):
    path = os.path.join("clips", filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Clip not found")
    return FileResponse(path)

# Health check
@app.get("/")
def root():
    return {"message": "Guardian Angel backend running"}
