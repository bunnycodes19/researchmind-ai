from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.evaluation import ActivityLog
from app.models.paper import Paper, PaperStatus
from app.repositories.chat_repository import ChatRepository
from app.repositories.paper_repository import PaperRepository


class DashboardService:
    def __init__(self, db: AsyncSession, user_id: UUID):
        self.db = db
        self.user_id = user_id
        self.paper_repo = PaperRepository(db)
        self.chat_repo = ChatRepository(db)

    async def get_stats(self) -> dict:
        papers = await self.paper_repo.list_by_user(self.user_id)
        processing = sum(1 for p in papers if p.status == PaperStatus.PROCESSING)
        chunks = await self.paper_repo.count_chunks_for_user(self.user_id)
        questions = await self.chat_repo.count_user_messages(self.user_id)
        storage = await self.paper_repo.total_storage_bytes(self.user_id)

        result = await self.db.execute(
            select(ActivityLog)
            .where(ActivityLog.user_id == self.user_id)
            .order_by(ActivityLog.created_at.desc())
            .limit(10)
        )
        activity = [
            {"action": a.action, "metadata": a.metadata_json, "created_at": a.created_at.isoformat()}
            for a in result.scalars().all()
        ]

        return {
            "total_papers": len(papers),
            "total_chunks": chunks,
            "questions_asked": questions,
            "papers_processing": processing,
            "storage_usage_bytes": storage,
            "recent_activity": activity,
        }
