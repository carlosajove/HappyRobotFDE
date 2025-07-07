from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class Load(BaseModel):
    load_id: int
    origin: str
    destination: str
    pickup_datetime: datetime
    delivery_datetime: datetime
    equipment_type: str
    loadboard_rate: float
    currency: float
    notes: Optional[str]
    weigth: float
    weigth_unit: float
    commodity_type: str
    num_of_pieces: int
    miles: int
    dimensions: str
    dimensions_unit: str

class CallData(BaseModel):
    call_id: Optional[int] = None
    carrier_mc: Optional[str] = None
    load_id: Optional[int] = None
    original_rate: Optional[float] = None
    negotiation_count: Optional[int] = 0
    counter_offers: Optional[int] = None
    final_rate: Optional[float] = None
    outcome: Optional[str] = None
    sentiment: Optional[str] = None

class CounterOffer(BaseModel):
    load_id: str
    offer_amount: int
    counter_offer_count: int
