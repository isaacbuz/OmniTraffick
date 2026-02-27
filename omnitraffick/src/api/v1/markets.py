"""Market API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from src.api.deps import get_db
from src.models.market import Market
from src.schemas.market import MarketCreate, MarketUpdate, MarketResponse

router = APIRouter(prefix="/markets", tags=["markets"])


@router.post("/", response_model=MarketResponse, status_code=201)
def create_market(market: MarketCreate, db: Session = Depends(get_db)):
    """Create a new market."""
    # Check if code already exists
    existing = db.query(Market).filter(Market.code == market.code).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Market with code '{market.code}' already exists")

    db_market = Market(**market.model_dump())
    db.add(db_market)
    db.commit()
    db.refresh(db_market)
    return db_market


@router.get("/", response_model=list[MarketResponse])
def list_markets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all markets."""
    markets = db.query(Market).offset(skip).limit(limit).all()
    return markets


@router.get("/{market_id}", response_model=MarketResponse)
def get_market(market_id: UUID, db: Session = Depends(get_db)):
    """Get a market by ID."""
    market = db.query(Market).filter(Market.id == market_id).first()
    if not market:
        raise HTTPException(status_code=404, detail="Market not found")
    return market


@router.put("/{market_id}", response_model=MarketResponse)
def update_market(market_id: UUID, market_update: MarketUpdate, db: Session = Depends(get_db)):
    """Update a market."""
    market = db.query(Market).filter(Market.id == market_id).first()
    if not market:
        raise HTTPException(status_code=404, detail="Market not found")

    update_data = market_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(market, key, value)

    db.commit()
    db.refresh(market)
    return market


@router.delete("/{market_id}", status_code=204)
def delete_market(market_id: UUID, db: Session = Depends(get_db)):
    """Delete a market."""
    market = db.query(Market).filter(Market.id == market_id).first()
    if not market:
        raise HTTPException(status_code=404, detail="Market not found")

    db.delete(market)
    db.commit()
    return None
