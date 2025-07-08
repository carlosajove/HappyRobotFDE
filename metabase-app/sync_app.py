import os
import requests
import sqlite3
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, HTTPException, Depends, Header

# Configuration
API_URL = os.getenv("API_URL")
API_KEY = os.getenv("API_KEY")
SYNC_API_KEY = os.getenv("SYNC_API_KEY")
LOCAL_DB = os.getenv("LOCAL_DB", "./analytics.db")

app = FastAPI(title="Analytics Sync Service", version="1.0.0")

def verify_api_key(api_key: str = Header(None)):
    """Verify API key for authentication"""
    if not SYNC_API_KEY:
        raise HTTPException(status_code=500, detail="API key not configured")
    if api_key != SYNC_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return api_key

def create_tables(conn):
    """Create tables in local database"""
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS loads (
            load_id INTEGER PRIMARY KEY,
            origin TEXT,
            destination TEXT,
            pickup_datetime TEXT,
            delivery_datetime TEXT,
            equipment_type TEXT,
            loadboard_rate REAL,
            currency TEXT,
            notes TEXT,
            weight REAL,
            weight_unit TEXT,
            commodity_type TEXT,
            num_of_pieces INTEGER,
            miles INTEGER,
            dimensions TEXT,
            dimensions_unit TEXT,
            synced_at TEXT
        )
    """)
    
    # Create call_sessions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS call_sessions (
            id INTEGER PRIMARY KEY,
            call_id TEXT,
            carrier_mc INTEGER,
            load_id INTEGER,
            original_rate REAL,
            final_rate REAL,
            negotiation_count INTEGER,
            outcome TEXT,
            sentiment TEXT,
            duration INTEGER,
            synced_at TEXT,
            FOREIGN KEY (load_id) REFERENCES loads (load_id)
        )
    """)
    
    conn.commit()

@app.get("/status")
def status(api_key: str = Depends(verify_api_key)):
    """Check configuration status"""
    return {
        "api_url": API_URL,
        "api_key_configured": bool(API_KEY),
        "sync_api_key_configured": bool(SYNC_API_KEY),
        "local_db": LOCAL_DB,
        "database_exists": Path(LOCAL_DB).exists()
    }

@app.post("/sync")
def sync_data(api_key: str = Depends(verify_api_key)):
    """Sync data from API to local database"""
    
    if not API_URL or not API_KEY:
        raise HTTPException(
            status_code=500, 
            detail="Missing required environment variables (API_URL, API_KEY)"
        )
    
    try:
        headers = {"api-key": API_KEY}
        
        # Fetch loads data
        loads_response = requests.get(f"{API_URL}/analytics/loads", headers=headers)
        if loads_response.status_code != 200:
            raise HTTPException(
                status_code=loads_response.status_code,
                detail=f"Error fetching loads data: {loads_response.text}"
            )
        
        # Fetch calls data
        calls_response = requests.get(f"{API_URL}/analytics/calls", headers=headers)
        if calls_response.status_code != 200:
            raise HTTPException(
                status_code=calls_response.status_code,
                detail=f"Error fetching calls data: {calls_response.text}"
            )
        
        loads_response_data = loads_response.json()
        calls_response_data = calls_response.json()
        
        # Extract the data arrays from the API response
        loads_data = loads_response_data.get("loads", [])
        calls_data = calls_response_data.get("call_sessions", [])
        
        conn = sqlite3.connect(LOCAL_DB)
        create_tables(conn)
        cursor = conn.cursor()
        
        sync_time = datetime.now().isoformat()
        
        for load in loads_data:
            cursor.execute("""
                INSERT OR REPLACE INTO loads (
                    load_id, origin, destination, pickup_datetime, delivery_datetime,
                    equipment_type, loadboard_rate, currency, notes, weight,
                    weight_unit, commodity_type, num_of_pieces, miles,
                    dimensions, dimensions_unit, synced_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                load["load_id"], load["origin"], load["destination"],
                load["pickup_datetime"], load["delivery_datetime"],
                load["equipment_type"], load["loadboard_rate"], load["currency"],
                load["notes"], load["weight"], load["weight_unit"],
                load["commodity_type"], load["num_of_pieces"], load["miles"],
                load["dimensions"], load["dimensions_unit"], sync_time
            ))
        
        for call in calls_data:
            cursor.execute("""
                INSERT OR REPLACE INTO call_sessions (
                    id, call_id, carrier_mc, load_id, original_rate, final_rate,
                    negotiation_count, outcome, sentiment, duration, synced_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                call["id"], call["call_id"], call["carrier_mc"], call["load_id"],
                call["original_rate"], call["final_rate"], call["negotiation_count"],
                call["outcome"], call["sentiment"], call["duration"], sync_time
            ))
        
        conn.commit()
        conn.close()
        
        return {
            "status": "success",
            "message": "Data sync completed successfully",
            "synced_at": sync_time,
            "loads_synced": len(loads_data),
            "calls_synced": len(calls_data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("� Starting Analytics Sync Service on port 8001")
    uvicorn.run(app, host="0.0.0.0", port=8001)
