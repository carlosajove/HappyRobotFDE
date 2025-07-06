import os, requests, uvicorn
from fastapi import FastAPI, Header, HTTPException, Depends
from app.db import SessionLocal, init_db, get_db, Load, CallSession
from dotenv import load_dotenv
from datetime import datetime

from app.security import verify_api_key
from .models import CounterOffer, CallData

load_dotenv() # only dev

API_KEY = os.getenv("API_KEY")
FMCSA_KEY = os.getenv("FMCSA_API_KEY")

app = FastAPI(title="FDE demo")
init_db()

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "fmcsa_key_configured": bool(FMCSA_KEY),
        "api_key_configured": bool(API_KEY)
    }

@app.get("/loads")
def get_loads(
    call_id: int, 
    origin: str = None,
    limit: int = 1,
    api_key: str = Depends(verify_api_key),
    db = Depends(get_db)
):
    query = db.query(Load)
    
    if origin:
        query = query.filter(Load.origin.ilike(f"%{origin}%"))
    
    loads = query.limit(limit).all()
    call_session = db.query(CallSession).filter(CallSession.call_id == call_id).first()

    return {
        "loads": [
            {
                "load_id": load.load_id,
                "origin": load.origin,
                "destination": load.destination,
                "pickup_datetime": load.pickup_datetime.isoformat(),
                "delivery_datetime": load.delivery_datetime.isoformat(),
                "equipment_type": load.equipment_type,
                "loadboard_rate": load.loadboard_rate,
                "initial_rate": 0.8*load.loadboard_rate,
                "currency": load.currency,
                "notes": load.notes,
                "weight": load.weight,
                "weight_unit": load.weight_unit,
                "commodity_type": load.commodity_type,
                "num_of_pieces": load.num_of_pieces,
                "miles": load.miles,
                "dimensions": load.dimensions,
                "dimensions_unit": load.dimensions_unit
            }
            for load in loads
        ],
        "total_found": len(loads)
    }

@app.post("/counter-offer")
def handle_counter_offer(counter_offer: CounterOffer, api_key: str = Depends(verify_api_key), db = Depends(get_db)):
    """Handle counter offer from carrier"""
    load_info = db.query(Load).filter(Load.load_id == counter_offer.load_id).first()
    if not load_info:
        raise HTTPException(status_code=404, detail="Load info not found")

    counter_offer.counter_offer_count += 1
    
    if counter_offer.offer_amount <= load_info.loadboard_rate:
        response = "accepted"
    elif counter_offer.counter_offer_count > 2:
        response = "rejected"
    else:
        response = "counter"
        suggested_rate = (0.8 + 0.2*(counter_offer.counter_offer_count/2)) * load_info.loadboard_rate

    db.commit()
    
    return {
        "response": response,
        "negotiation_count": counter_offer.counter_offer_count,
        "suggested_rate":  suggested_rate if response == "counter" else None
    }

@app.get("/verify-mc")
def verify_mc(mc: int, api_key: str = Depends(verify_api_key), db = Depends(get_db)):
    if not FMCSA_KEY:
        raise HTTPException(status_code=500, detail="FMCSA API key not configured")

    url = f"https://mobile.fmcsa.dot.gov/qc/services/carriers/docket-number/{mc}?webKey={FMCSA_KEY}"
    
    new_session = CallSession(
        carrier_mc=mc
    )

    db.add(new_session)
    db.commit()
    return {'response': True, 'call_id': new_session.call_id}

@app.post("/call/start")
def start_call(api_key: str = Depends(verify_api_key), db = Depends(get_db)):
    call_session = CallSession()
    db.add(call_session)
    db.commit()
    return {
        'status': 'successfull',
        'call_id': call_session.call_id,
    }


@app.post("/call/end")
def end_call(call_data: CallData, db = Depends(get_db)):
    """End call and extract final data"""
    call_session = db.query(CallSession).filter(CallSession.call_id == call_data.call_id).first()
    if not call_session:
        raise HTTPException(status_code=404, detail="Call session not found")
    
    call_session.final_rate = call_data.final_rate
    call_session.outcome = call_data.outcome
    call_session.sentiment = call_data.sentiment
    call_session.notes = call_data.notes
    call_session.end_time = datetime.utcnow()
    
    db.commit()
    
    return {
        "call_id": call_data.call_id,
        "status": "call_ended",
        "outcome": call_data.outcome,
        "sentiment": call_data.sentiment,
        "transfer_needed": call_data.outcome == "accepted"
    }

if __name__ == "__main__":       
    uvicorn.run("app.main:app",host="0.0.0.0",port=8080,reload=False)