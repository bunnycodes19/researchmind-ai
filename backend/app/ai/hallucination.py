import json

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from app.config import get_settings


class HallucinationDetector:
    def __init__(self) -> None:
        settings = get_settings()
        self.llm = ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            google_api_key=settings.google_api_key,
            temperature=0,
        )

    async def verify(self, answer: str, context_chunks: list[dict]) -> tuple[float, bool]:
        context = "\n".join(c["metadata"].get("content", "")[:500] for c in context_chunks[:5])
        prompt = (
            "Given CONTEXT and ANSWER, rate faithfulness 0.0-1.0 "
            "(1.0 = fully supported). Reply JSON: {\"confidence\": float, \"supported\": bool}\n\n"
            f"CONTEXT:\n{context}\n\nANSWER:\n{answer}"
        )
        try:
            resp = await self.llm.ainvoke(
                [SystemMessage(content="JSON only."), HumanMessage(content=prompt)]
            )
            text = resp.content.strip()
            if "```" in text:
                text = text.split("```")[1].replace("json", "", 1)
            data = json.loads(text)
            confidence = float(data.get("confidence", 0.5))
            supported = bool(data.get("supported", confidence >= 0.6))
            return confidence, not supported or confidence < 0.55
        except Exception:
            return 0.5, False
