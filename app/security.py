import os
from dotenv import load_dotenv
from fastapi import Header, HTTPException


def verify_api_key(api_key: str = Header(None)):
    """Verify API key for authentication"""
    API_KEY = os.getenv("API_KEY")
    if not API_KEY:
        raise HTTPException(status_code=500, detail="API key not configured")
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return api_key