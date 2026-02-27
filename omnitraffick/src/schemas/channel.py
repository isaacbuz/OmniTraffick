"""Pydantic schemas for Channel."""
from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime


class ChannelBase(BaseModel):
    """Base Channel schema."""

    platform_name: str
    api_identifier: str


class ChannelCreate(ChannelBase):
    """Schema for creating a Channel."""

    pass


class ChannelUpdate(BaseModel):
    """Schema for updating a Channel."""

    platform_name: str | None = None
    api_identifier: str | None = None


class ChannelResponse(ChannelBase):
    """Schema for Channel response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime
