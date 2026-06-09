from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.rag_chain import RAGChain
from app.ai.retriever import RetrieverService
from app.models.artifacts import Flashcard, LiteratureReview, StudyNote, Summary
from app.repositories.paper_repository import PaperRepository

PROMPTS = {
    "summary": (
        "Generate executive summary JSON with keys: executive_summary, key_contributions, "
        "methodology, results, limitations, future_work, research_impact"
    ),
    "flashcards": "Generate JSON: {cards: [{front, back}]} with 10 flashcards.",
    "quiz": "Generate JSON: {questions: [{question, options, answer}]} with 8 quiz questions.",
    "interview": "Generate JSON: {questions: [string]} with 12 technical interview questions.",
    "notes": "Generate JSON: {sections: [{title, bullets}]} study notes.",
    "revision": "Generate JSON: {topics: [{name, key_points}]} exam revision sheet.",
    "cheatsheet": "Generate JSON: {sections: [{title, formulas_and_facts}]} cheat sheet.",
    "literature": (
        "Generate literature review JSON: background, research_gap, existing_methods, "
        "comparative_analysis, future_directions, references"
    ),
}


class StudyService:
    def __init__(self, db: AsyncSession, user_id: UUID):
        self.db = db
        self.user_id = user_id
        self.paper_repo = PaperRepository(db)
        self.retriever = RetrieverService(user_id)
        self.chain = RAGChain()

    async def _get_hits(self, paper_id: UUID, task: str) -> list[dict]:
        paper = await self.paper_repo.get_owned(paper_id, self.user_id)
        from app.models.paper import PaperStatus

        if not paper or paper.status != PaperStatus.READY:
            raise ValueError("Paper not ready")
        return await self.retriever.retrieve(task, [paper_id])

    async def generate_summary(self, paper_id: UUID) -> Summary:
        hits = await self._get_hits(paper_id, "Summarize this research paper comprehensively")
        content = await self.chain.generate_structured(PROMPTS["summary"], hits)
        row = Summary(user_id=self.user_id, paper_id=paper_id, content=content)
        self.db.add(row)
        await self.db.flush()
        return row

    async def generate_study(self, paper_id: UUID, artifact_type: str) -> StudyNote | Flashcard:
        key = artifact_type if artifact_type in PROMPTS else "notes"
        hits = await self._get_hits(paper_id, f"Generate {artifact_type} for this paper")
        content = await self.chain.generate_structured(PROMPTS.get(key, PROMPTS["notes"]), hits)
        if artifact_type == "flashcards":
            row = Flashcard(user_id=self.user_id, paper_id=paper_id, cards=content.get("cards", content))
            self.db.add(row)
            await self.db.flush()
            return row
        row = StudyNote(
            user_id=self.user_id,
            paper_id=paper_id,
            note_type=artifact_type,
            content=content,
        )
        self.db.add(row)
        await self.db.flush()
        return row

    async def generate_literature_review(self, paper_ids: list[UUID]) -> LiteratureReview:
        hits = await self.retriever.retrieve("Literature review across papers", paper_ids)
        content = await self.chain.generate_structured(PROMPTS["literature"], hits)
        row = LiteratureReview(user_id=self.user_id, paper_ids=paper_ids, content=content)
        self.db.add(row)
        await self.db.flush()
        return row
