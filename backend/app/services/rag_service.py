from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.agent import run_research_agent
from app.ai.evaluation import RAGEvaluationService
from app.ai.hallucination import HallucinationDetector
from app.ai.rag_chain import RAGChain
from app.ai.retriever import RetrieverService
from app.core.middleware import sanitize_user_prompt
from app.models.evaluation import Evaluation
from app.repositories.chat_repository import ChatRepository
from app.repositories.paper_repository import PaperRepository


class RAGService:
    def __init__(self, db: AsyncSession, user_id: UUID):
        self.db = db
        self.user_id = user_id
        self.retriever = RetrieverService(user_id)
        self.chain = RAGChain()
        self.detector = HallucinationDetector()
        self.evaluator = RAGEvaluationService()
        self.chat_repo = ChatRepository(db)
        self.paper_repo = PaperRepository(db)

    async def ask(
        self,
        session_id: UUID,
        content: str,
        mode: str = "expert",
        paper_ids: list[UUID] | None = None,
    ) -> dict:
        session = await self.chat_repo.get_session(session_id, self.user_id)
        if not session:
            raise ValueError("Session not found")

        scope = paper_ids or (list(session.paper_ids) if session.paper_ids else None)
        if scope:
            papers = await self.paper_repo.get_many_owned(scope, self.user_id)
            from app.models.paper import PaperStatus

            scope = [p.id for p in papers if p.status == PaperStatus.READY]

        question = sanitize_user_prompt(content)
        await self.chat_repo.add_message(session_id, "user", question, mode=mode)

        hits = await self.retriever.retrieve(question, scope)
        reranked = await self.retriever.rerank(question, hits)
        answer, citations = await self.chain.generate_answer(question, reranked, mode)
        confidence, low_warning = await self.detector.verify(answer, reranked)

        assistant = await self.chat_repo.add_message(
            session_id,
            "assistant",
            answer,
            citations=citations,
            confidence=confidence,
            mode=mode,
        )

        contexts = [h["metadata"].get("content", "") for h in reranked]
        metrics = await self.evaluator.evaluate_turn(question, answer, contexts)
        self.db.add(
            Evaluation(
                message_id=assistant.id,
                relevance=metrics.get("relevance"),
                faithfulness=metrics.get("faithfulness"),
                context_precision=metrics.get("context_precision"),
                context_recall=metrics.get("context_recall"),
            )
        )
        await self.db.flush()

        return {
            "message": assistant,
            "low_confidence_warning": low_warning,
        }

    async def compare_papers(self, paper_ids: list[UUID], question: str | None) -> dict:
        q = question or "Compare these research papers across methodology, datasets, results, and limitations."
        report = await run_research_agent(self.user_id, q, paper_ids)
        hits = await self.retriever.retrieve(q, paper_ids)
        structured = await self.chain.generate_structured(
            "Return JSON: {comparison_table: [{dimension, values: {paper_title: value}}], narrative: string}",
            hits,
        )
        return {
            "comparison_table": structured.get("comparison_table", []),
            "narrative": report or structured.get("narrative", ""),
            "citations": [],
        }
