"""Channel model - represents advertising platforms."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.database import Base


class Channel(Base):
    """Channel model for advertising platforms."""

    __tablename__ = "channels"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    platform_name = Column(String(100), nullable=False)
    api_identifier = Column(String(100), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    tickets = relationship("Ticket", back_populates="channel", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Channel {self.platform_name} ({self.api_identifier})>"
