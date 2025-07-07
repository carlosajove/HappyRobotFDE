from datetime import datetime
from fastapi import Depends, APIRouter
from app.db import get_db, Load, CallSession
from app.security import verify_api_key

router = APIRouter()


@router.get("/analytics/loads")
def get_analytics_data(api_key: str = Depends(verify_api_key), db = Depends(get_db)):
    """Export loads data for analytics dashboard"""
    
    loads = db.query(Load).all()
    loads_data = [
        {
            "load_id": load.load_id,
            "origin": load.origin,
            "destination": load.destination,
            "pickup_datetime": load.pickup_datetime.isoformat(),
            "delivery_datetime": load.delivery_datetime.isoformat(),
            "equipment_type": load.equipment_type,
            "loadboard_rate": load.loadboard_rate,
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
    ]
    return {
        "loads": loads_data,
    }

@router.get("/analytics/calls")
def get_analytics_data(api_key: str = Depends(verify_api_key), db = Depends(get_db)):
    """Export loads calls for analytics dashboard"""

    call_sessions = db.query(CallSession).all()
    calls_data = [
        {
            "id": call.id,
            "call_id": call.call_id,
            "carrier_mc": call.carrier_mc,
            "load_id": call.load_id,
            "original_rate": call.original_rate,
            "final_rate": call.final_rate,
            "negotiation_count": call.negotiation_count,
            "outcome": call.outcome,
            "sentiment": call.sentiment,
            "duration": call.duration
        }
        for call in call_sessions
    ]
    
    return {
        "call_sessions": calls_data,
    }