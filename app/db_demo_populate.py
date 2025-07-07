from datetime import datetime
from fastapi import Depends, APIRouter
from app.db import get_db, Load, CallSession
from app.security import verify_api_key
from app.demo_data.demo_calls import demo_calls
from app.demo_data.demo_loads import demo_loads

router = APIRouter()

@router.post("/populate-demo-loads")
def populate_demo_loads(api_key: str = Depends(verify_api_key), db = Depends(get_db)):
    try:
        existing_loads = db.query(Load).count()
        if existing_loads > 0:
            return {
                "message": "Demo loads already exist",
            }
        
        for load_data in demo_loads:
            load = Load(**load_data)
            db.add(load)
        
        db.commit()
        
        return {
            "message": "Demo loads populated successfully",
        }
    except Exception as e: 
        return {
            "message": "An error ocurred while loading the demo data",
            "error": f"{e}"
        }


@router.post("/populate-demo-calls")
def populate_demo_calls(api_key: str = Depends(verify_api_key), db = Depends(get_db)):
    try:
        existing_calls = db.query(CallSession).count()
        if existing_calls > 0:
            return {
                "message": "Demo calls already exist",
                "existing_count": existing_calls
            }
        
        existing_loads = db.query(Load).all()
        if not existing_loads:
            return {
                "message": "No loads found. Please populate demo loads first.",
                "error": "run /populate-demo-loads first"
            }
        
        for call_data in demo_calls:
            call_session = CallSession(**call_data)
            db.add(call_session)
        
        db.commit()
        
        return {
            "message": "Demo call sessions populated successfully",
        }
    except Exception as e: 
        return {
            "message": "An error occurred while loading the demo call data",
            "error": f"{e}"
        }

@router.post("/populate-all-demo-data")
def populate_all_demo_data(api_key: str = Depends(verify_api_key), db = Depends(get_db)):
    """Populate both loads and call sessions"""
    try:
        populate_demo_loads(api_key, db)
        populate_demo_calls(api_key, db)
        
        return {
            "message": "All demo data populated successfully",
        }
    except Exception as e:
        return {
            "message": "An error occurred while populating all demo data",
            "error": f"{e}"
        }