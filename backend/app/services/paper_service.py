from pathlib import Path
from uuid import UUID, uuid4

import aiofiles
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.evaluation import ActivityLog
from app.models.paper import PaperStatus
from app.repositories.paper_repository import PaperRepository
from app.services.processing_service import ProcessingService


class PaperService:
    ALLOWED_CONTENT = {"application/pdf"}

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = PaperRepository(db)
        self.settings = get_settings()

    async def upload_many(
        self, user_id: UUID, files: list[UploadFile], background_tasks=None
    ) -> list:
        count = await self.repo.count_by_user(user_id)
        if count + len(files) > self.settings.max_papers_per_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Paper limit reached for your account",
            )

        upload_dir = Path(self.settings.upload_dir) / str(user_id)
        upload_dir.mkdir(parents=True, exist_ok=True)

        papers = []
        for file in files:
            if file.content_type not in self.ALLOWED_CONTENT:
                raise HTTPException(status_code=400, detail=f"Invalid file type: {file.filename}")
            content = await file.read()
            if len(content) > self.settings.max_upload_bytes:
                raise HTTPException(status_code=400, detail="File too large")

            paper_id = uuid4()
            safe_name = f"{paper_id}_{file.filename}"
            path = upload_dir / safe_name
            async with aiofiles.open(path, "wb") as f:
                await f.write(content)

            title = (file.filename or "paper.pdf").replace(".pdf", "").replace("_", " ")
            paper = await self.repo.create(
                user_id=user_id,
                title=title,
                filename=file.filename or "paper.pdf",
                file_path=str(path),
                file_size_bytes=len(content),
            )
            self.db.add(
                ActivityLog(user_id=user_id, action="paper_uploaded", metadata_json={"paper_id": str(paper.id)})
            )
            papers.append(paper)
            if background_tasks is not None:
                background_tasks.add_task(self._process_background, paper.id, user_id)
            else:
                await self._process_background(paper.id, user_id)

        return papers

    async def _process_background(self, paper_id: UUID, user_id: UUID) -> None:
        from app.db.session import AsyncSessionLocal

        async with AsyncSessionLocal() as session:
            try:
                await ProcessingService(session).process_paper(paper_id, user_id)
                await session.commit()
            except Exception:
                await session.rollback()

    async def delete(self, user_id: UUID, paper_id: UUID) -> None:
        paper = await self.repo.get_owned(paper_id, user_id)
        if not paper:
            raise HTTPException(status_code=404, detail="Paper not found")
        from app.ai.vector_store import FaissVectorStore

        FaissVectorStore(user_id).remove_paper(paper_id)
        path = Path(paper.file_path)
        if path.exists():
            path.unlink()
        await self.repo.delete(paper)
