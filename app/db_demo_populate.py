from datetime import datetime
from fastapi import Depends, APIRouter
from app.db import get_db, Load
from app.security import verify_api_key

router = APIRouter()

@router.post("/populate-demo-loads")
def populate_demo_loads(api_key: str = Depends(verify_api_key), db = Depends(get_db)):
    try:
        existing_loads = db.query(Load).count()
        if existing_loads > 0:
            return {
                "message": "Demo loads already exist",
            }
        
        demo_loads = [
            {
                "load_id": 1001,
                "origin": "RIVERDALE, GA",
                "destination": "ATLANTA, GA", 
                "pickup_datetime": datetime(2025, 7, 8, 10, 0),
                "delivery_datetime": datetime(2025, 7, 8, 18, 0),
                "equipment_type": "Van",
                "loadboard_rate": 1500.0,
                "currency": "USD",
                "notes": "Electronics shipment - handle with care",
                "weight": 15000.0,
                "weight_unit": "lbs",
                "commodity_type": "Electronics",
                "num_of_pieces": 25,
                "miles": 35,
                "dimensions": "48x40x60",
                "dimensions_unit": "inches"
            },
            {
                "load_id": 1002,
                "origin": "CHICAGO, IL",
                "destination": "MILWAUKEE, WI",
                "pickup_datetime": datetime(2025, 7, 9, 8, 0),
                "delivery_datetime": datetime(2025, 7, 9, 14, 0),
                "equipment_type": "Flatbed",
                "loadboard_rate": 800.0,
                "currency": "USD",
                "notes": "",
                "weight": 25000.0,
                "weight_unit": "lbs",
                "commodity_type": "Construction Materials",
                "num_of_pieces": 10,
                "miles": 92,
                "dimensions": "48x102x8",
                "dimensions_unit": "inches"
            },
            {
                "load_id": 1003,
                "origin": "DALLAS, TX",
                "destination": "HOUSTON, TX",
                "pickup_datetime": datetime(2025, 7, 10, 12, 0),
                "delivery_datetime": datetime(2025, 7, 10, 20, 0),
                "equipment_type": "Reefer",
                "loadboard_rate": 1200.0,
                "currency": "USD",
                "notes": "Frozen goods - maintain -10°F",
                "weight": 20000.0,
                "weight_unit": "lbs",
                "commodity_type": "Frozen Food",
                "num_of_pieces": 100,
                "miles": 240,
                "dimensions": "48x40x72",
                "dimensions_unit": "inches"
            },
            {
                "load_id": 1004,
                "origin": "PHOENIX, AZ",
                "destination": "LAS VEGAS, NV",
                "pickup_datetime": datetime(2025, 7, 11, 6, 0),
                "delivery_datetime": datetime(2025, 7, 11, 16, 0),
                "equipment_type": "Van",
                "loadboard_rate": 900.0,
                "currency": "USD",
                "notes": "",
                "weight": 18000.0,
                "weight_unit": "lbs",
                "commodity_type": "Retail Goods",
                "num_of_pieces": 45,
                "miles": 295,
                "dimensions": "48x40x65",
                "dimensions_unit": "inches"
            }
        ]
        
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