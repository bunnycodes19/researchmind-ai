from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.paper import PaperStatus


class PaperResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    filename: str
    file_size_bytes: int
    page_count: int
    status: PaperStatus
    processing_error: str | None
    metadata_json: dict | None
    created_at: datetime


class PaperListResponse(BaseModel):
    items: list[PaperResponse]
    total: int


class PaperUploadResponse(BaseModel):
    papers: list[PaperResponse]
    message: str


class ComparePapersRequest(BaseModel):
    paper_ids: list[UUID] = Field(min_length=2, max_length=10)
    question: str | None = None


class ComparePapersResponse(BaseModel):
    comparison_table: list[dict]
    narrative: str
    citations: list[dict]
