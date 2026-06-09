from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, File, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.repositories.paper_repository import PaperRepository
from app.schemas.paper import ComparePapersRequest, ComparePapersResponse, PaperListResponse, PaperResponse, PaperUploadResponse
from app.services.paper_service import PaperService
from app.services.rag_service import RAGService

router = APIRouter(prefix="/papers", tags=["papers"])


@router.get("", response_model=PaperListResponse)
async def list_papers(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    items = await PaperRepository(db).list_by_user(user.id)
    return PaperListResponse(items=items, total=len(items))


@router.get("/{paper_id}", response_model=PaperResponse)
async def get_paper(
    paper_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    paper = await PaperRepository(db).get_owned(paper_id, user.id)
    if not paper:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Paper not found")
    return paper


@router.post("/upload", response_model=PaperUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_papers(
    background_tasks: BackgroundTasks,
    files: list[UploadFile] = File(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    papers = await PaperService(db).upload_many(user.id, files, background_tasks)
    return PaperUploadResponse(papers=papers, message="Upload successful. Processing started.")


@router.delete("/{paper_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_paper(
    paper_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await PaperService(db).delete(user.id, paper_id)


@router.post("/compare", response_model=ComparePapersResponse)
async def compare_papers(
    body: ComparePapersRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await RAGService(db, user.id).compare_papers(body.paper_ids, body.question)
    return ComparePapersResponse(**result)
