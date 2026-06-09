import re
from uuid import UUID

from app.ai.embeddings import EmbeddingService
from app.ai.vector_store import FaissVectorStore
from app.config import get_settings


class RetrieverService:
    def __init__(self, user_id: UUID):
        self.user_id = user_id
        self.embeddings = EmbeddingService()
        self.store = FaissVectorStore(user_id)
        self.settings = get_settings()

    def _keywords(self, query: str) -> list[str]:
        tokens = re.findall(r"[a-zA-Z0-9]{4,}", query.lower())
        return list(dict.fromkeys(tokens))[:12]

    async def retrieve(
        self,
        query: str,
        paper_ids: list[UUID] | None = None,
    ) -> list[dict]:
        vector = await self.embeddings.embed_query(query)
        raw = self.store.hybrid_search(
            vector,
            self._keywords(query),
            k=self.settings.retrieval_top_k,
            paper_ids=paper_ids,
        )
        return [{"metadata": m, "score": s} for m, s in raw]

    async def rerank(self, query: str, hits: list[dict]) -> list[dict]:
        if not hits:
            return []
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.messages import HumanMessage

        settings = get_settings()
        llm = ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            google_api_key=settings.google_api_key,
            temperature=0,
        )

        snippets = []
        for i, h in enumerate(hits[: self.settings.retrieval_top_k]):
            m = h["metadata"]
            snippets.append(f"[{i}] {m.get('content', '')[:400]}")

        prompt = (
            f"Question: {query}\n\n"
            "Rank these snippets 0-N by relevance (most relevant first). "
            "Reply with comma-separated indices only.\n\n"
            + "\n\n".join(snippets)
        )
        try:
            resp = await llm.ainvoke([HumanMessage(content=prompt)])
            order = [int(x.strip()) for x in resp.content.split(",") if x.strip().isdigit()]
            reranked = [hits[i] for i in order if i < len(hits)]
            for h in hits:
                if h not in reranked:
                    reranked.append(h)
            return reranked[: self.settings.rerank_top_k]
        except Exception:
            return hits[: self.settings.rerank_top_k]
