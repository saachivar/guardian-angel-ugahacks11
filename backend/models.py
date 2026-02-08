from pydantic import BaseModel

class EventCreate(BaseModel):
    timestamp: str
    confidence: float
    clip_path: str
    device_id: str

class Event(EventCreate):
    id: int
    resolved: int 

class SignupRequest(BaseModel):
    username: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str
