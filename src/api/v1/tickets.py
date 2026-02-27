"""Ticket API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from src.api.deps import get_db
from src.models.ticket import Ticket
from src.models.campaign import Campaign
from src.models.channel import Channel
from src.schemas.ticket import TicketCreate, TicketUpdate, TicketResponse

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post("/", response_model=TicketResponse, status_code=201)
def create_ticket(ticket: TicketCreate, db: Session = Depends(get_db)):
    """Create a new ticket."""
    # Validate campaign exists
    campaign = db.query(Campaign).filter(Campaign.id == ticket.campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=422, detail="Invalid campaign_id: campaign does not exist")

    # Validate channel exists
    channel = db.query(Channel).filter(Channel.id == ticket.channel_id).first()
    if not channel:
        raise HTTPException(status_code=422, detail="Invalid channel_id: channel does not exist")

    db_ticket = Ticket(**ticket.model_dump())
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket


@router.get("/", response_model=list[TicketResponse])
def list_tickets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all tickets."""
    tickets = db.query(Ticket).offset(skip).limit(limit).all()
    return tickets


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(ticket_id: UUID, db: Session = Depends(get_db)):
    """Get a ticket by ID."""
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.put("/{ticket_id}", response_model=TicketResponse)
def update_ticket(ticket_id: UUID, ticket_update: TicketUpdate, db: Session = Depends(get_db)):
    """Update a ticket (status, external_platform_id, qa_failure_reason)."""
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    update_data = ticket_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(ticket, key, value)

    db.commit()
    db.refresh(ticket)
    return ticket


@router.delete("/{ticket_id}", status_code=204)
def delete_ticket(ticket_id: UUID, db: Session = Depends(get_db)):
    """Delete a ticket."""
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    db.delete(ticket)
    db.commit()
    return None
