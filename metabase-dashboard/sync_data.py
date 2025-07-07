#!/usr/bin/env python3
"""
Script to sync data from HappyRobot FDE API to a local SQLite database for Metabase
"""
import os
import requests
import sqlite3
import json
from datetime import datetime
from pathlib import Path

# Configuration - Docker will load env vars from .env file
API_URL = os.getenv("API_URL")
API_KEY = os.getenv("API_KEY")
LOCAL_DB = os.getenv("LOCAL_DB", "analytics.db")

# Ensure the database is created in the current working directory
if not os.path.isabs(LOCAL_DB):
    LOCAL_DB = os.path.join(os.getcwd(), LOCAL_DB.split('/')[-1])

print(f"📄 Using database: {LOCAL_DB}")

if not API_URL or not API_KEY:
    print("❌ Error: Missing required environment variables (API_URL, API_KEY)")
    exit(1)

def create_tables(conn):
    """Create tables in local database"""
    cursor = conn.cursor()
    
    # Create loads table
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

def sync_data():
    """Sync data from API to local database"""
    
    headers = {"api-key": API_KEY}
    
    # Fetch loads data
    loads_response = requests.get(f"{API_URL}/analytics/loads", headers=headers)
    if loads_response.status_code != 200:
        print(f"Error fetching loads data: {loads_response.status_code}")
        print(loads_response.text)
        return
    
    # Fetch calls data
    calls_response = requests.get(f"{API_URL}/analytics/calls", headers=headers)
    if calls_response.status_code != 200:
        print(f"Error fetching calls data: {calls_response.status_code}")
        print(calls_response.text)
        return
    
    loads_response_data = loads_response.json()
    calls_response_data = calls_response.json()
    
    # Extract the data arrays from the API response
    loads_data = loads_response_data.get("loads", [])
    calls_data = calls_response_data.get("call_sessions", [])
    
    conn = sqlite3.connect(LOCAL_DB)
    create_tables(conn)
    cursor = conn.cursor()
    
    sync_time = datetime.now().isoformat()
    
    # Sync loads data (INSERT OR REPLACE for upsert behavior)
    print(f"Syncing {len(loads_data)} loads...")
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
    
    # Sync calls data (INSERT OR REPLACE for upsert behavior)
    print(f"Syncing {len(calls_data)} call sessions...")
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
    
    print("✅ Data sync completed successfully.")

if __name__ == "__main__":
    try:
        sync_data()
    except Exception as e:
        print(f"❌ Error: {e}")
