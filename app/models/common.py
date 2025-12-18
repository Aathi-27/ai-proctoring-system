from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class Role(str, Enum):
    ADMIN = "ADMIN"
    CANDIDATE = "CANDIDATE"
    INVIGILATOR = "INVIGILATOR"


class RiskClassification(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Recommendation(str, Enum):
    PASS = "PASS"
    REVIEW = "REVIEW"
    FLAG_FOR_REVIEW = "FLAG_FOR_REVIEW"


class User(BaseModel):
    user_id: str
    role: Role
    monitored_exam_ids: list[str] = Field(default_factory=list)


class SoftDeleteMetadata(BaseModel):
    deleted_at: datetime | None = None
    expires_at: datetime | None = None
