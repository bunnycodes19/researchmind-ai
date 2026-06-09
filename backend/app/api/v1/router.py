from fastapi import APIRouter

from app.api.v1 import auth, chat, dashboard, papers, study

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(papers.router)
api_router.include_router(chat.router)
api_router.include_router(study.router)
api_router.include_router(dashboard.router)
