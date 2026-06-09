from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.repositories.chat_repository import ChatRepository
from app.schemas.chat import (
    AskResponse,
    ChatSessionCreate,
    ChatSessionResponse,
    MessageCreate,
    MessageResponse,
)
from app.services.rag_service import RAGService

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/sessions", response_model=list[ChatSessionResponse])
async def list_sessions(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await ChatRepository(db).list_sessions(user.id)


@router.post("/sessions", response_model=ChatSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    body: ChatSessionCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ChatRepository(db).create_session(
        user.id, body.title or "New conversation", body.paper_ids
    )


@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
async def get_session(
    session_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    session = await ChatRepository(db).get_session(session_id, user.id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.get("/sessions/{session_id}/messages", response_model=list[MessageResponse])
async def list_messages(
    session_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    session = await ChatRepository(db).get_session(session_id, user.id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session.messages


@router.post("/sessions/{session_id}/messages", response_model=AskResponse)
async def send_message(
    session_id: UUID,
    body: MessageCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        result = await RAGService(db, user.id).ask(
            session_id, body.content, body.mode or "expert", body.paper_ids
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return AskResponse(message=result["message"], low_confidence_warning=result["low_confidence_warning"])
