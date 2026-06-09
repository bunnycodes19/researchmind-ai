from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import Citation


class ChatSessionCreate(BaseModel):
    title: str | None = "New conversation"
    paper_ids: list[UUID] | None = None


class ChatSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    paper_ids: list[UUID] | None
    created_at: datetime


class MessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=16000)
    mode: str | None = Field(default="expert", pattern="^(simple|intermediate|expert)$")
    paper_ids: list[UUID] | None = None


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    role: str
    content: str
    citations: list[Citation] | list[dict] | None
    confidence: float | None
    mode: str | None
    created_at: datetime


class AskResponse(BaseModel):
    message: MessageResponse
    low_confidence_warning: bool = False
