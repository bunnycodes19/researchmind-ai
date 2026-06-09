from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.evaluation import Evaluation
from app.models.user import User
from app.schemas.dashboard import DashboardStats, EvaluationResponse
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
async def stats(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await DashboardService(db, user.id).get_stats()


@router.get("/evaluations/{message_id}", response_model=EvaluationResponse)
async def get_evaluation(
    message_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Evaluation).where(Evaluation.message_id == message_id))
    ev = result.scalar_one_or_none()
    if not ev:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    return EvaluationResponse(
        message_id=str(ev.message_id),
        relevance=ev.relevance,
        faithfulness=ev.faithfulness,
        context_precision=ev.context_precision,
        context_recall=ev.context_recall,
    )
