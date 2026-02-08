"""
Guardian Angel - Data Receiver Service
Receives fall detection data from Raspberry Pi and forwards to main backend
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional
import requests
import logging
from datetime import datetime
import os
import shutil

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Guardian Angel Data Receiver")

# Directory to save uploaded video clips
CLIPS_DIR = os.path.join(os.path.dirname(__file__), "clips")
os.makedirs(CLIPS_DIR, exist_ok=True)

# Main backend URL (update this to your main backend's address)
MAIN_BACKEND_URL = "http://localhost:8000/events"

# Data models
class FallDetectionData(BaseModel):
    confidence: float
    clip_path: str
    device_id: str
    timestamp: Optional[str] = None
    auto_call: bool = True  # Default to triggering calls
    location: Optional[str] = None
    
class HealthCheckResponse(BaseModel):
    status: str
    service: str
    timestamp: str
    main_backend: str

@app.get("/")
def root():
    """Health check endpoint"""
    return HealthCheckResponse(
        status="online",
        service="Guardian Angel Data Receiver",
        timestamp=datetime.now().isoformat(),
        main_backend=MAIN_BACKEND_URL
    )

@app.post("/receive-fall-detection")
async def receive_fall_detection(data: FallDetectionData):
    """
    Receives fall detection data from Raspberry Pi or other devices
    and forwards it to the main backend with Twilio integration
    
    DEPRECATED: Use /upload endpoint instead for video uploads
    """
    logger.info(f"📥 Received fall detection from {data.device_id}")
    logger.info(f"   Confidence: {data.confidence}")
    logger.info(f"   Clip: {data.clip_path}")
    logger.info(f"   Auto-call: {data.auto_call}")
    
    # Add timestamp if not provided
    if not data.timestamp:
        data.timestamp = datetime.now().isoformat()
    
    # Prepare data for main backend
    payload = {
        "confidence": data.confidence,
        "clip_path": data.clip_path,
        "device_id": data.device_id,
        "timestamp": data.timestamp,
        "auto_call": data.auto_call
    }
    
    try:
        # Forward to main backend
        logger.info(f"📤 Forwarding to main backend: {MAIN_BACKEND_URL}")
        response = requests.post(MAIN_BACKEND_URL, json=payload, timeout=10)
        
        if response.status_code == 200:
            logger.info("✅ Successfully forwarded to main backend")
            backend_response = response.json()
            
            # Log call results if emergency calls were made
            if backend_response.get("emergency_calls"):
                for call in backend_response["emergency_calls"]:
                    if call.get("success"):
                        logger.info(f"📞 Called {call['contact']} at {call['phone']}")
                    else:
                        logger.error(f"❌ Failed to call {call['contact']}: {call.get('error')}")
            
            return {
                "status": "success",
                "message": "Fall detection received and forwarded",
                "received_at": datetime.now().isoformat(),
                "backend_response": backend_response
            }
        else:
            logger.error(f"❌ Main backend returned error: {response.status_code}")
            raise HTTPException(
                status_code=502,
                detail=f"Main backend error: {response.status_code}"
            )
            
    except requests.exceptions.ConnectionError:
        logger.error("❌ Cannot connect to main backend - is it running?")
        raise HTTPException(
            status_code=503,
            detail="Main backend is not available. Please ensure it's running."
        )
    except requests.exceptions.Timeout:
        logger.error("❌ Main backend timeout")
        raise HTTPException(
            status_code=504,
            detail="Main backend timeout"
        )
    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal error: {str(e)}"
        )

@app.post("/upload")
async def upload_fall_detection(
    file: UploadFile = File(...),
    device_id: str = Form(...),
    confidence: float = Form(...),
    timestamp: Optional[str] = Form(None),
    auto_call: bool = Form(True)
):
    

    """
    NEW ENDPOINT: Receives fall detection with video file upload
    
    This matches the format from your other server:
    - Multipart form data with video file
    - device_id, confidence, timestamp as form fields
    
    Example usage from Raspberry Pi:
        files = {"file": (filename, f, "video/mp4")}
        data = {"device_id": "pi_01", "confidence": 0.95, "timestamp": "..."}
        requests.post(url, files=files, data=data)
    """
    
    logger.info("=" * 60)
    logger.info(f"📥 NEW FALL DETECTION RECEIVED")
    logger.info(f"   Device: {device_id}")
    logger.info(f"   Confidence: {confidence}")
    logger.info(f"   Timestamp: {timestamp or 'auto-generated'}")
    logger.info(f"   Auto-call: {auto_call}")
    logger.info(f"   Video file: {file.filename}")
    logger.info(f"   File size: {file.size if hasattr(file, 'size') else 'unknown'} bytes")
    logger.info("=" * 60)
    
    # Generate timestamp if not provided
    if not timestamp:
        timestamp = datetime.now().isoformat()
    
    
    # Save uploaded video file
    try:
        # Create safe filename
        safe_filename = f"{device_id}_{timestamp.replace(':', '-').replace('.', '_')}.mp4"
        file_path = os.path.join(CLIPS_DIR, safe_filename)
        
        logger.info(f"💾 Saving video to: {file_path}")
        
        # Save the uploaded file
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
            shutil.copyfileobj(file.file, buffer)
        
        file_size = os.path.getsize(file_path)
        logger.info(f"✅ Video saved successfully ({file_size} bytes)")
        
    except Exception as e:
        logger.error(f"❌ Failed to save video: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save video file: {str(e)}"
        )
    
    # Prepare data for main backend
    payload = {
        "confidence": float(confidence),
        "clip_path": file_path,  # Local path to saved video
        "device_id": device_id,
        "timestamp": timestamp,
        "auto_call": bool(auto_call)
    }
    
    try:
        # Forward to main backend
        logger.info(f"📤 Forwarding to main backend: {MAIN_BACKEND_URL}")
        response = requests.post(MAIN_BACKEND_URL, json=payload, timeout=15)
        
        if response.status_code == 200:
            logger.info("✅ Successfully forwarded to main backend")
            backend_response = response.json()
            
            # Log call results if emergency calls were made
            if backend_response.get("emergency_calls"):
                logger.info("📞 EMERGENCY CALLS INITIATED:")
                for call in backend_response["emergency_calls"]:
                    if call.get("success"):
                        logger.info(f"   ✅ Called {call['contact']} at {call['phone']}")
                        logger.info(f"      Execution SID: {call.get('execution_sid')}")
                    else:
                        logger.error(f"   ❌ Failed to call {call['contact']}: {call.get('error')}")
            else:
                logger.info("ℹ️  No emergency calls made (auto_call was False)")
            
            logger.info("=" * 60)
            
            return {
                "status": "success",
                "message": "Fall detection received, video saved, and forwarded to backend",
                "received_at": datetime.now().isoformat(),
                "video_saved_to": file_path,
                "video_size_bytes": file_size,
                "backend_response": backend_response
            }
        else:
            logger.error(f"❌ Main backend returned error: {response.status_code}")
            logger.error(f"   Response: {response.text}")
            raise HTTPException(
                status_code=502,
                detail=f"Main backend error: {response.status_code}"
            )
            
    except requests.exceptions.ConnectionError:
        logger.error("❌ Cannot connect to main backend - is it running?")
        raise HTTPException(
            status_code=503,
            detail="Main backend is not available. Please ensure it's running on port 8000."
        )
    except requests.exceptions.Timeout:
        logger.error("❌ Main backend timeout")
        raise HTTPException(
            status_code=504,
            detail="Main backend timeout - it took too long to respond"
        )
    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Internal error: {str(e)}"
        )

@app.post("/test")
async def test_endpoint():
    """
    Test endpoint to verify the receiver is working
    Sends a test fall detection to the main backend
    """
    logger.info("🧪 Test endpoint called")
    
    test_data = FallDetectionData(
        confidence=0.99,
        clip_path="clips/test_fall.mp4",
        device_id="test_device",
        timestamp=datetime.now().isoformat(),
        auto_call=False,  # Don't actually call during tests
        location="Test Location"
    )
    
    return await receive_fall_detection(test_data)

@app.get("/health")
def health_check():
    """Detailed health check"""
    try:
        # Try to reach main backend
        response = requests.get("http://localhost:8000/", timeout=2)
        main_backend_status = "online" if response.status_code == 200 else "error"
    except:
        main_backend_status = "offline"
    
    return {
        "receiver_status": "online",
        "main_backend_status": main_backend_status,
        "main_backend_url": MAIN_BACKEND_URL,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
