import hashlib
from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.repositories.user_repository import UserRepository
from app.schemas.common import TokenResponse, UserCreate


class AuthService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)
        self.db = db

    async def signup(self, data: UserCreate) -> TokenResponse:
        existing = await self.repo.get_by_email(data.email)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
        user = await self.repo.create(data.email, hash_password(data.password), data.full_name)
        return await self._issue_tokens(user.id)

    async def login(self, email: str, password: str) -> TokenResponse:
        user = await self.repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        return await self._issue_tokens(user.id)

    async def refresh(self, refresh_token: str) -> TokenResponse:
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        stored = await self.repo.get_valid_refresh(token_hash)
        if not stored:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
        return await self._issue_tokens(stored.user_id)

    async def logout(self, user_id: UUID) -> None:
        await self.repo.revoke_refresh_tokens(user_id)

    async def _issue_tokens(self, user_id: UUID) -> TokenResponse:
        access = create_access_token(user_id)
        refresh = create_refresh_token(user_id)
        token_hash = hashlib.sha256(refresh.encode()).hexdigest()
        expires = datetime.now(timezone.utc) + timedelta(days=7)
        await self.repo.save_refresh_token(user_id, token_hash, expires)
        return TokenResponse(access_token=access, refresh_token=refresh)
