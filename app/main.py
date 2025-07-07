import os, requests, uvicorn
from fastapi import FastAPI, Header, HTTPException, Depends
from app.db import SessionLocal, init_db, get_db, Load, CallSession
from dotenv import load_dotenv
from datetime import datetime

from app.security import verify_api_key
from app.models import CounterOffer, CallData
from app.db_demo_populate import router as demo_router

load_dotenv() # only dev

API_KEY = os.getenv("API_KEY")
FMCSA_KEY = os.getenv("FMCSA_API_KEY")

app = FastAPI(title="FDE demo")
app.include_router(demo_router)
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
    origin: str = None,
    limit: int = 1,
    api_key: str = Depends(verify_api_key),
    db = Depends(get_db)
):
    query = db.query(Load)
    
    if origin:
        query = query.filter(Load.origin.ilike(f"%{origin}%"))
    
    loads = query.limit(limit).all()

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
    
    try:
        response = requests.get(url)
        response.raise_for_status()
    
        data = response.json()
        carrier = data["content"][0]["carrier"]
        response = {
            "verified": True if (carrier.get("allowedToOperate") == 'Y') else False,
            "mc_number": mc,
            "allowedToOperate": carrier.get("allowedToOperate"),
            "legalName": carrier.get("legalName"),
            "dbaName": carrier.get("dbaName"),
            "listedCity": carrier.get("phyCity"),
            "listedState": carrier.get("phyState"),
        }
        return response
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error verifying MC: {str(e)}")


@app.post("/call/start")
def start_call(api_key: str = Depends(verify_api_key), db = Depends(get_db)):
    call_session = CallSession()
    db.add(call_session)
    db.commit()
    return {
        'status': 'successfull',
        'call_id': call_session.id,
    }


@app.post("/call/end")
def end_call(call_data: CallData, db = Depends(get_db)):
    """End call and extract final data"""

    call_session = CallSession()
    call_session.call_id = call_data.call_id
    call_session.carrier_mc = call_data.carrier_mc
    call_session.load_id = call_data.load_id
    call_session.original_rate = call_data.original_rate
    call_session.final_rate = call_data.final_rate
    call_session.negotiation_count = call_data.negotiation_count
    call_session.outcome = call_data.outcome
    call_session.sentiment = call_data.sentiment
    call_session.duration = call_data.duration
    
    db.commit()
    
    return {
        'response': "success",
    }

if __name__ == "__main__":       
    uvicorn.run("app.main:app",host="0.0.0.0",port=8080,reload=False)