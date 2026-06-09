from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class GenerateSummaryRequest(BaseModel):
    paper_id: UUID


class GenerateStudyRequest(BaseModel):
    paper_id: UUID
    artifact_type: str = Field(
        pattern="^(flashcards|quiz|interview|notes|revision|cheatsheet)$"
    )


class LiteratureReviewRequest(BaseModel):
    paper_ids: list[UUID] = Field(min_length=1, max_length=10)


class ArtifactResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    content: dict | list
    created_at: datetime
