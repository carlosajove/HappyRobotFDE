# db.py
from datetime import datetime
from typing import Optional
import os

from sqlalchemy import Column, Integer, String, Float, DateTime, create_engine, Text, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

if os.getenv("FLY_APP_NAME"):
    DATABASE_URL = "sqlite:///:memory:"
else:
    DATABASE_URL = "sqlite:///loads_demo.db"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

def init_db():
    """Initialize the database by creating all tables."""
    Base.metadata.create_all(engine)

def get_db():
    """Get database session with auto-initialization."""
    # Ensure tables exist for in-memory database
    if "memory" in DATABASE_URL:
        Base.metadata.create_all(engine)
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Load(Base):
    __tablename__ = "loads"

    id = Column(Integer, primary_key=True)
    load_id = Column(Integer, unique=True, nullable=False)
    origin = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    pickup_datetime = Column(DateTime, nullable=False)
    delivery_datetime = Column(DateTime, nullable=False)
    equipment_type = Column(String, nullable=False)
    loadboard_rate = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False)
    notes = Column(String)
    weight = Column(Float, nullable=False)
    weight_unit = Column(String, nullable=False)
    commodity_type = Column(String, nullable=False)
    num_of_pieces = Column(Integer, nullable=False)
    miles = Column(Integer, nullable=False)
    dimensions = Column(String, nullable=False)
    dimensions_unit = Column(String, nullable=False)


class CallSession(Base):
    __tablename__ = "call_sessions"
    
    id = Column(Integer, primary_key=True)
    call_id = Column(Integer, unique=True, autoincrement=True)
    carrier_mc = Column(String)
    load_id = Column(Integer, ForeignKey('loads.load_id'))
    original_rate = Column(Float)
    final_rate = Column(Float)
    outcome = Column(String)
    sentiment = Column(String)
    negotiation_count = Column(Integer, default=0)
    start_time = Column(DateTime, default=datetime.now())
    end_time = Column(DateTime)
    
    load = relationship("Load", backref="call_sessions")