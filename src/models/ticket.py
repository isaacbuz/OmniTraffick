"""Ticket model - represents trafficking requests."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum as python_enum

from src.database import Base


class TicketStatus(python_enum.Enum):
    """Ticket status enum."""

    DRAFT = "DRAFT"
    QA_TESTING = "QA_TESTING"
    QA_FAILED = "QA_FAILED"
    READY_FOR_API = "READY_FOR_API"
    TRAFFICKED_SUCCESS = "TRAFFICKED_SUCCESS"
    FAILED = "FAILED"


class Ticket(Base):
    """Ticket model for trafficking requests."""

    __tablename__ = "tickets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False)
    channel_id = Column(UUID(as_uuid=True), ForeignKey("channels.id"), nullable=False)
    request_type = Column(String(100), nullable=False)
    payload_config = Column(JSON, nullable=False)
    status = Column(Enum(TicketStatus), default=TicketStatus.DRAFT, nullable=False)
    external_platform_id = Column(String(200), nullable=True)
    qa_failure_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    campaign = relationship("Campaign", back_populates="tickets")
    channel = relationship("Channel", back_populates="tickets")

    def __repr__(self):
        return f"<Ticket {self.id} [{self.status.value}]>"
