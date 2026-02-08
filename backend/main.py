# main.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import os
from twilio.rest import Client
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ------------------------------
# 1️⃣ MongoDB Setup
# ------------------------------
MONGO_URI = "mongodb+srv://db_user:db_pass@guardian-angel.k4xhwty.mongodb.net/"
client = MongoClient(MONGO_URI)
db = client["guardian_angel"]
events_collection = db["events"]

# ------------------------------
# 2️⃣ Twilio Setup
# ------------------------------
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "YOUR_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "YOUR_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "+18442398571")
TWILIO_FLOW_SID = os.getenv("TWILIO_FLOW_SID", "YOUR_FLOW_SID")

# Primary and secondary caregiver contacts
PRIMARY_CONTACT = {
    "name": "Stuti Thummala",
    "phone": "+14708073876"
}
SECONDARY_CONTACT = {
    "name": "Saachi Varshney", 
    "phone": "+14705536461"
}
PATIENT_NAME = "Anisha Dhawan"

twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# ------------------------------
# 3️⃣ FastAPI Setup
# ------------------------------
app = FastAPI(title="Guardian Angel Backend")

# ------------------------------
# 3️⃣ FastAPI Setup
# ------------------------------
app = FastAPI(title="Guardian Angel Backend")

# ------------------------------
# 4️⃣ Helper Functions
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

def make_emergency_call(phone_number: str, contact_name: str):
    """
    Trigger Twilio Studio Flow to call a caregiver.
    The flow should have TTS configured to say:
    "Anisha Dhawan has fallen down. Please check your Guardian Angel app."
    """
    try:
        execution = twilio_client.studio.v2.flows(TWILIO_FLOW_SID) \
            .executions \
            .create(
                to=phone_number,
                from_=TWILIO_PHONE_NUMBER
            )
        
        logger.info(f"✅ Emergency call initiated to {contact_name} ({phone_number}): {execution.sid}")
        return {
            "success": True,
            "execution_sid": execution.sid,
            "contact": contact_name,
            "phone": phone_number
        }
    except Exception as e:
        logger.error(f"❌ Failed to call {contact_name}: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "contact": contact_name,
            "phone": phone_number
        }

# ------------------------------
# 5️⃣ API Endpoints
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
        "device_id": "pi01",
        "auto_call": true  # optional, triggers emergency calls
    }
    """
    if "timestamp" not in event or not event["timestamp"]:
        event["timestamp"] = datetime.now().isoformat()

    event["resolved"] = 0

    result = events_collection.insert_one(event)

    # 📞 Trigger emergency calls if requested
    call_results = []
    if event.get("auto_call", False):
        logger.info("🚨 FALL DETECTED - Initiating emergency calls...")
        
        # Call primary contact
        primary_result = make_emergency_call(
            PRIMARY_CONTACT["phone"], 
            PRIMARY_CONTACT["name"]
        )
        call_results.append(primary_result)
        
        # Call secondary contact
        secondary_result = make_emergency_call(
            SECONDARY_CONTACT["phone"],
            SECONDARY_CONTACT["name"]
        )
        call_results.append(secondary_result)

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
        },
        "emergency_calls": call_results if call_results else None
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

# Test emergency calling system
@app.post("/test-call")
def test_emergency_call(contact: str = "primary"):
    """
    Test the emergency calling system.
    Query param: contact = "primary" | "secondary" | "both"
    """
    results = []
    
    if contact in ["primary", "both"]:
        result = make_emergency_call(
            PRIMARY_CONTACT["phone"],
            PRIMARY_CONTACT["name"]
        )
        results.append(result)
    
    if contact in ["secondary", "both"]:
        result = make_emergency_call(
            SECONDARY_CONTACT["phone"],
            SECONDARY_CONTACT["name"]
        )
        results.append(result)
    
    return {
        "test": "emergency_call",
        "contact_tested": contact,
        "results": results
    }
