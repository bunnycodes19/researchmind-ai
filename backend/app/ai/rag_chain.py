import json
from uuid import UUID

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from app.config import get_settings

MODE_INSTRUCTIONS = {
    "simple": "Explain in beginner-friendly English (ELI5). Avoid jargon.",
    "intermediate": "Explain clearly for someone with undergraduate STEM background.",
    "expert": "Use precise academic language appropriate for researchers.",
}


class RAGChain:
    def __init__(self) -> None:
        settings = get_settings()
        self.llm = ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            google_api_key=settings.google_api_key,
            temperature=0.2,
        )

    def _build_context(self, hits: list[dict]) -> str:
        blocks = []
        for i, h in enumerate(hits):
            m = h["metadata"]
            blocks.append(
                f"[Source {i + 1}] Paper: {m.get('paper_title')} | "
                f"Page {m.get('page_number')} | Section: {m.get('section_name')}\n"
                f"{m.get('content', '')}"
            )
        return "\n\n---\n\n".join(blocks)

    async def generate_answer(
        self,
        question: str,
        hits: list[dict],
        mode: str = "expert",
    ) -> tuple[str, list[dict]]:
        context = self._build_context(hits)
        mode_inst = MODE_INSTRUCTIONS.get(mode, MODE_INSTRUCTIONS["expert"])

        system = (
            "You are ResearchMind AI, a research paper assistant. "
            "Answer ONLY using the provided context. "
            "Include inline citations like [Source N]. "
            "If context is insufficient, say so explicitly. "
            f"{mode_inst}\n\n"
            "Return JSON: {\"answer\": string, \"citations\": [{\"source_index\": int, \"page\": int, \"excerpt\": string}]}"
        )
        user = f"Context:\n{context}\n\nQuestion: {question}"

        resp = await self.llm.ainvoke([SystemMessage(content=system), HumanMessage(content=user)])
        text = resp.content.strip()
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        try:
            data = json.loads(text)
            answer = data.get("answer", text)
            raw_citations = data.get("citations", [])
        except json.JSONDecodeError:
            answer = text
            raw_citations = []

        citations = []
        for c in raw_citations:
            idx = int(c.get("source_index", 1)) - 1
            if 0 <= idx < len(hits):
                m = hits[idx]["metadata"]
                citations.append(
                    {
                        "chunk_id": m.get("chunk_id"),
                        "paper_id": m.get("paper_id"),
                        "paper_title": m.get("paper_title"),
                        "page_number": c.get("page") or m.get("page_number"),
                        "section_name": m.get("section_name"),
                        "excerpt": c.get("excerpt") or m.get("content", "")[:240],
                    }
                )
        return answer, citations

    async def generate_structured(
        self,
        task_prompt: str,
        hits: list[dict],
    ) -> dict:
        context = self._build_context(hits)
        system = "Return valid JSON only. Use only provided context."
        user = f"Context:\n{context}\n\nTask:\n{task_prompt}"
        resp = await self.llm.ainvoke([SystemMessage(content=system), HumanMessage(content=user)])
        text = resp.content.strip()
        if "```" in text:
            text = text.split("```")[1].replace("json", "", 1)
        return json.loads(text)
