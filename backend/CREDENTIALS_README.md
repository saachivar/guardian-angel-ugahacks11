# Twilio Credentials Setup

## IMPORTANT: The `.env` file contains your actual Twilio credentials

The `.env` file in this directory contains your real Twilio credentials and is **NOT tracked by Git** (it's in `.gitignore`).

### Credentials are stored in `.env`:
The `.env` file contains all your Twilio API credentials including:
- Account SID
- Auth Token  
- Phone Number
- Studio Flow SID

**These credentials are safe because:**
- ✅ `.env` is in `.gitignore` - never committed to Git
- ✅ Only exists on your local machine
- ✅ Backend loads them automatically using python-dotenv

### How it works:
1. The `.env` file is loaded automatically by `python-dotenv`
2. The `main.py` file reads credentials using `os.getenv()`
3. If `.env` is missing, it falls back to placeholder values

### To run the backend:
```bash
# Install dependencies (includes python-dotenv)
pip3 install -r requirements.txt

# Start the server (will automatically load .env)
python3 -m uvicorn main:app --reload --port 8000
```

### For deployment or other developers:
1. Copy `.env.example` to `.env`
2. Replace the placeholder values with actual Twilio credentials
3. Never commit the `.env` file to Git

### Emergency calls will work because:
- ✅ `.env` file exists locally with real credentials
- ✅ Git ignores `.env` file (protected by `.gitignore`)
- ✅ GitHub push protection won't block commits
- ✅ Backend loads credentials automatically on startup
