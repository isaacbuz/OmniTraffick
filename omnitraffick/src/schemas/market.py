"""Pydantic schemas for Market."""
from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime


class MarketBase(BaseModel):
    """Base Market schema."""

    code: str
    country: str
    region: str


class MarketCreate(MarketBase):
    """Schema for creating a Market."""

    pass


class MarketUpdate(BaseModel):
    """Schema for updating a Market."""

    code: str | None = None
    country: str | None = None
    region: str | None = None


class MarketResponse(MarketBase):
    """Schema for Market response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime
