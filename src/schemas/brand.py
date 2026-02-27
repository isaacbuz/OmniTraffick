"""Pydantic schemas for Brand."""
from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime


class BrandBase(BaseModel):
    """Base Brand schema."""

    name: str
    internal_code: str


class BrandCreate(BrandBase):
    """Schema for creating a Brand."""

    pass


class BrandUpdate(BaseModel):
    """Schema for updating a Brand."""

    name: str | None = None
    internal_code: str | None = None


class BrandResponse(BrandBase):
    """Schema for Brand response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime
