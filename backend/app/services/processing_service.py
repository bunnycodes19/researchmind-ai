from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.embeddings import EmbeddingService
from app.ai.knowledge_extractor import KnowledgeExtractor
from app.ai.vector_store import FaissVectorStore
from app.config import get_settings
from app.models.paper import Chunk, Embedding, Paper, PaperStatus
from app.pipeline.chunker import chunk_pages
from app.pipeline.pdf_extractor import extract_pdf_text
from app.repositories.paper_repository import PaperRepository


class ProcessingService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.paper_repo = PaperRepository(db)
        self.settings = get_settings()

    async def process_paper(self, paper_id: UUID, user_id: UUID) -> Paper:
        paper = await self.paper_repo.get_owned(paper_id, user_id)
        if not paper:
            raise ValueError("Paper not found")

        await self.paper_repo.update_status(paper, PaperStatus.PROCESSING)

        try:
            await self.db.execute(delete(Embedding).where(Embedding.chunk_id.in_(select(Chunk.id).where(Chunk.paper_id == paper.id))))
            await self.db.execute(delete(Chunk).where(Chunk.paper_id == paper.id))
            FaissVectorStore(user_id).remove_paper(paper_id)

            pages, page_count, title = extract_pdf_text(paper.file_path)
            paper.page_count = page_count
            if title and title != "Untitled Paper":
                paper.title = title

            text_chunks = chunk_pages(
                pages,
                chunk_size=self.settings.chunk_size,
                overlap=self.settings.chunk_overlap,
            )

            embedding_svc = EmbeddingService()
            store = FaissVectorStore(user_id)
            texts = [c.content for c in text_chunks]
            vectors = await embedding_svc.embed_documents(texts)

            db_chunks: list[Chunk] = []
            metadatas: list[dict] = []
            for text_chunk in text_chunks:
                db_chunk = Chunk(
                    paper_id=paper.id,
                    chunk_index=text_chunk.chunk_index,
                    content=text_chunk.content,
                    page_number=text_chunk.page_number,
                    section_name=text_chunk.section_name,
                    char_start=text_chunk.char_start,
                    char_end=text_chunk.char_end,
                )
                self.db.add(db_chunk)
                await self.db.flush()
                db_chunks.append(db_chunk)
                metadatas.append(
                    {
                        "chunk_id": str(db_chunk.id),
                        "paper_id": str(paper.id),
                        "paper_title": paper.title,
                        "page_number": text_chunk.page_number,
                        "section_name": text_chunk.section_name,
                        "content": text_chunk.content,
                    }
                )

            faiss_indices = store.add_vectors(vectors, metadatas)
            for db_chunk, faiss_idx in zip(db_chunks, faiss_indices):
                self.db.add(
                    Embedding(
                        chunk_id=db_chunk.id,
                        faiss_index=faiss_idx,
                        dimension=len(vectors[0]),
                    )
                )

            sample = "\n".join(texts[:5])[:12000]
            paper.metadata_json = await KnowledgeExtractor().extract(sample)

            await self.paper_repo.update_status(paper, PaperStatus.READY)
            await self.db.flush()
            return paper
        except Exception as e:
            await self.paper_repo.update_status(paper, PaperStatus.FAILED, str(e))
            await self.db.flush()
            return paper
