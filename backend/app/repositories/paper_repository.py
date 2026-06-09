from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.paper import Chunk, Paper, PaperStatus


class PaperRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def count_by_user(self, user_id: UUID) -> int:
        result = await self.db.execute(
            select(func.count()).select_from(Paper).where(Paper.user_id == user_id)
        )
        return result.scalar() or 0

    async def list_by_user(self, user_id: UUID) -> list[Paper]:
        result = await self.db.execute(
            select(Paper).where(Paper.user_id == user_id).order_by(Paper.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_owned(self, paper_id: UUID, user_id: UUID) -> Paper | None:
        result = await self.db.execute(
            select(Paper).where(Paper.id == paper_id, Paper.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_many_owned(self, paper_ids: list[UUID], user_id: UUID) -> list[Paper]:
        result = await self.db.execute(
            select(Paper).where(Paper.id.in_(paper_ids), Paper.user_id == user_id)
        )
        return list(result.scalars().all())

    async def create(
        self,
        user_id: UUID,
        title: str,
        filename: str,
        file_path: str,
        file_size_bytes: int,
    ) -> Paper:
        paper = Paper(
            user_id=user_id,
            title=title,
            filename=filename,
            file_path=file_path,
            file_size_bytes=file_size_bytes,
            status=PaperStatus.PENDING,
        )
        self.db.add(paper)
        await self.db.flush()
        return paper

    async def update_status(
        self, paper: Paper, status: PaperStatus, error: str | None = None
    ) -> Paper:
        paper.status = status
        paper.processing_error = error
        await self.db.flush()
        return paper

    async def delete(self, paper: Paper) -> None:
        await self.db.delete(paper)

    async def get_with_chunks(self, paper_id: UUID, user_id: UUID) -> Paper | None:
        result = await self.db.execute(
            select(Paper)
            .options(selectinload(Paper.chunks))
            .where(Paper.id == paper_id, Paper.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def count_chunks_for_user(self, user_id: UUID) -> int:
        result = await self.db.execute(
            select(func.count())
            .select_from(Chunk)
            .join(Paper)
            .where(Paper.user_id == user_id)
        )
        return result.scalar() or 0

    async def total_storage_bytes(self, user_id: UUID) -> int:
        result = await self.db.execute(
            select(func.coalesce(func.sum(Paper.file_size_bytes), 0)).where(Paper.user_id == user_id)
        )
        return int(result.scalar() or 0)
