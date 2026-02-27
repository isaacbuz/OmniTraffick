"""Pydantic schemas for Ticket."""
from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Any
from src.models.ticket import TicketStatus


class TicketBase(BaseModel):
    """Base Ticket schema."""

    campaign_id: UUID
    channel_id: UUID
    request_type: str
    payload_config: dict[str, Any]


class TicketCreate(TicketBase):
    """Schema for creating a Ticket."""

    pass


class TicketUpdate(BaseModel):
    """Schema for updating a Ticket."""

    status: TicketStatus | None = None
    external_platform_id: str | None = None
    qa_failure_reason: str | None = None


class TicketResponse(BaseModel):
    """Schema for Ticket response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    campaign_id: UUID
    channel_id: UUID
    request_type: str
    payload_config: dict[str, Any]
    status: TicketStatus
    external_platform_id: str | None
    qa_failure_reason: str | None
    created_at: datetime
    updated_at: datetime
