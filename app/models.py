from datetime import datetime, timezone
from typing import List
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class GenerateSectionRequest(BaseModel):
    company_id: str = Field(...)
    section_type: str = Field(...)
    text: str = Field(...)


class GenerateSectionResponse(BaseModel):
    request_id: UUID = Field(default_factory=uuid4)
    company_id: str
    section_type: str
    generated_text: str
    sources: List[str]
    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))


class HistoryItem(BaseModel):
    request_id: UUID
    section_type: str
    generated_text: str
    created_at: datetime
    sources: List[str]


class HistoryResponse(BaseModel):
    company_id: str
    items: List[HistoryItem]
