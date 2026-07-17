import json
import uuid
from datetime import datetime
from typing import Any, Dict, Optional
from decimal import Decimal
from pydantic import BaseModel, Field
from sqlalchemy import CLOB, Column, Numeric, String, TIMESTAMP, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import TypeDecorator

Base = declarative_base()


class JsonCLOB(TypeDecorator):
    """Serialize structured values into the CLOB columns used by Oracle."""

    impl = CLOB
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":")) if value is not None else None

    def process_result_value(self, value, dialect):
        return json.loads(value) if value else None

# ============================================================================
# SQLAlchemy ORM Model
# ============================================================================
class VideoORM(Base):
    """
    SQLAlchemy Model representing the 'videos' table.
    Matches the deployed Oracle ``videos`` table.
    """
    __tablename__ = "videos"

    id = Column(
        String(36),
        primary_key=True, 
        default=lambda: str(uuid.uuid4),
        index=True
    )
    prompt = Column(CLOB, nullable=False)
    status = Column(String(50), default="pending", nullable=False)
    slides_data = Column(JsonCLOB, nullable=True)
    error_message = Column(CLOB, nullable=True)
    cold_start_time = Column(Numeric(10, 3), nullable=True)
    rendering_time = Column(Numeric(10, 3), nullable=True)
    video_length = Column(Numeric(10, 3), nullable=True)
    resources_used = Column(JsonCLOB, nullable=True)
    video_storage_url = Column(String(2048), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.current_timestamp())

    def to_dict(self) -> Dict[str, Any]:
        """Convert ORM model to dictionary."""
        return {
            "id": str(self.id),
            "prompt": self.prompt,
            "status": self.status,
            "slides_data": self.slides_data,
            "error_message": self.error_message,
            "cold_start_time": self.cold_start_time,
            "rendering_time": self.rendering_time,
            "video_length": self.video_length,
            "resources_used": self.resources_used,
            "video_storage_url": self.video_storage_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


# ============================================================================
# Pydantic Schemas for Validation and Serialization
# ============================================================================
class VideoBase(BaseModel):
    prompt: str = Field(..., description="The prompt used to generate the video.")
    status: str = Field("pending", max_length=50, description="Processing status of the video.")
    slides_data: Optional[list] = Field(None, description="Generated slides narration and content data.")
    error_message: Optional[str] = Field(None, description="Any error encountered during generation.")
    cold_start_time: Optional[Decimal] = Field(None, max_digits=10, decimal_places=3, description="Cold start time in seconds.")
    rendering_time: Optional[Decimal] = Field(None, max_digits=10, decimal_places=3, description="Rendering duration in seconds.")
    video_length: Optional[Decimal] = Field(None, max_digits=10, decimal_places=3, description="Duration of the video in seconds.")
    resources_used: Optional[Dict[str, Any]] = Field(None, description="Metrics capturing RAM/CPU spikes or other system resources.")
    video_storage_url: Optional[str] = Field(None, max_length=2048, description="Reference URL where the final video file is stored.")

class VideoCreate(VideoBase):
    pass

class VideoResponse(VideoBase):
    id: str = Field(..., min_length=36, max_length=36)
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: str,
        }
