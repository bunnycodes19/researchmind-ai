from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.chat import ChatSession, Message


class ChatRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_session(
        self, user_id: UUID, title: str, paper_ids: list[UUID] | None
    ) -> ChatSession:
        session = ChatSession(user_id=user_id, title=title, paper_ids=paper_ids)
        self.db.add(session)
        await self.db.flush()
        return session

    async def list_sessions(self, user_id: UUID) -> list[ChatSession]:
        result = await self.db.execute(
            select(ChatSession).where(ChatSession.user_id == user_id).order_by(ChatSession.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_session(self, session_id: UUID, user_id: UUID) -> ChatSession | None:
        result = await self.db.execute(
            select(ChatSession)
            .options(selectinload(ChatSession.messages))
            .where(ChatSession.id == session_id, ChatSession.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def add_message(
        self,
        session_id: UUID,
        role: str,
        content: str,
        citations: list | None = None,
        confidence: float | None = None,
        mode: str | None = None,
    ) -> Message:
        msg = Message(
            session_id=session_id,
            role=role,
            content=content,
            citations=citations,
            confidence=confidence,
            mode=mode,
        )
        self.db.add(msg)
        await self.db.flush()
        return msg

    async def count_user_messages(self, user_id: UUID) -> int:
        result = await self.db.execute(
            select(func.count())
            .select_from(Message)
            .join(ChatSession)
            .where(ChatSession.user_id == user_id, Message.role == "user")
        )
        return result.scalar() or 0
