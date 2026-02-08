from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pymongo import MongoClient
from datetime import datetime
import os
import requests

# ------------------------------
# MongoDB setup
# ------------------------------
MONGO_URI = "mongodb+srv://db_user:db_pass@guardian-angel.k4xhwty.mongodb.net/"
client = MongoClient(MONGO_URI)
db = client["guardian_angel"]
events_collection = db["events"]

# ------------------------------
# FastAPI app
# ------------------------------
app = FastAPI(title="Guardian Angel Backend")

# Flutter backend URL
FLUTTER_SERVER_URL = "http://172.20.114.28:8000/upload"

# ------------------------------
# Helpers
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
# Upload endpoint
# ------------------------------
@app.post("/upload")
async def upload_event(
    device_id: str = Form(...),
    confidence: float = Form(...),
    timestamp: str = Form(None),
    file: UploadFile = File(...)
):
    # Ensure clips folder exists
    os.makedirs("clips", exist_ok=True)

    # Use current time if no timestamp provided
    if not timestamp:
        timestamp = datetime.now().isoformat()

    # Save file locally
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

    # Insert into MongoDB
    result = events_collection.insert_one(event)
    saved_event = events_collection.find_one({"_id": result.inserted_id})

    # ------------------------------
    # Forward to Flutter backend
    # ------------------------------
    try:
        with open(path, "rb") as f:
            files = {"file": (filename, f, "video/mp4")}
            data = {
                "device_id": device_id,
                "confidence": confidence,
                "timestamp": timestamp
            }

            resp = requests.post(FLUTTER_SERVER_URL, files=files, data=data, timeout=120)

            if not resp.ok:
                # Log it on the server
                print("Flutter status:", resp.status_code)
                print("Flutter body:", resp.text)

                # Send the REAL error back to the client
                raise HTTPException(
                    status_code=resp.status_code,
                    detail=f"Flutter error {resp.status_code}: {resp.text}"
                )

            # If Flutter returns JSON
            try:
                flutter_response = resp.json()
            except ValueError:
                flutter_response = {"raw_response": resp.text}

    except requests.exceptions.RequestException as e:
        print("Network error talking to Flutter:", repr(e))
        # Network-level error (can't connect, timeout, etc)
        raise HTTPException(
            status_code=502,
            detail=f"Could not reach Flutter backend: {str(e)}"
        )

    # ------------------------------
    # Success response
    # ------------------------------
    return {
        "status": "success",
        "id": str(result.inserted_id),
        "event": serialize_event(saved_event),
        "flutter_response": flutter_response
    }
