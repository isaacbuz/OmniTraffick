"""Channel API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from src.api.deps import get_db
from src.models.channel import Channel
from src.schemas.channel import ChannelCreate, ChannelUpdate, ChannelResponse

router = APIRouter(prefix="/channels", tags=["channels"])


@router.post("/", response_model=ChannelResponse, status_code=201)
def create_channel(channel: ChannelCreate, db: Session = Depends(get_db)):
    """Create a new channel."""
    # Check if api_identifier already exists
    existing = db.query(Channel).filter(Channel.api_identifier == channel.api_identifier).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Channel with api_identifier '{channel.api_identifier}' already exists",
        )

    db_channel = Channel(**channel.model_dump())
    db.add(db_channel)
    db.commit()
    db.refresh(db_channel)
    return db_channel


@router.get("/", response_model=list[ChannelResponse])
def list_channels(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all channels."""
    channels = db.query(Channel).offset(skip).limit(limit).all()
    return channels


@router.get("/{channel_id}", response_model=ChannelResponse)
def get_channel(channel_id: UUID, db: Session = Depends(get_db)):
    """Get a channel by ID."""
    channel = db.query(Channel).filter(Channel.id == channel_id).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    return channel


@router.put("/{channel_id}", response_model=ChannelResponse)
def update_channel(channel_id: UUID, channel_update: ChannelUpdate, db: Session = Depends(get_db)):
    """Update a channel."""
    channel = db.query(Channel).filter(Channel.id == channel_id).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    update_data = channel_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(channel, key, value)

    db.commit()
    db.refresh(channel)
    return channel


@router.delete("/{channel_id}", status_code=204)
def delete_channel(channel_id: UUID, db: Session = Depends(get_db)):
    """Delete a channel."""
    channel = db.query(Channel).filter(Channel.id == channel_id).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    db.delete(channel)
    db.commit()
    return None
