from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.study import ArtifactResponse, GenerateStudyRequest, GenerateSummaryRequest, LiteratureReviewRequest
from app.services.study_service import StudyService

router = APIRouter(prefix="/study", tags=["study"])


@router.post("/summary", response_model=ArtifactResponse)
async def summary(
    body: GenerateSummaryRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        row = await StudyService(db, user.id).generate_summary(body.paper_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return ArtifactResponse(id=row.id, content=row.content, created_at=row.created_at)


@router.post("/generate", response_model=ArtifactResponse)
async def generate_study(
    body: GenerateStudyRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        row = await StudyService(db, user.id).generate_study(body.paper_id, body.artifact_type)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    content = row.cards if hasattr(row, "cards") else row.content
    return ArtifactResponse(id=row.id, content=content, created_at=row.created_at)


@router.post("/literature-review", response_model=ArtifactResponse)
async def literature_review(
    body: LiteratureReviewRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        row = await StudyService(db, user.id).generate_literature_review(body.paper_ids)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return ArtifactResponse(id=row.id, content=row.content, created_at=row.created_at)
