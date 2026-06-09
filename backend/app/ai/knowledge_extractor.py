import json

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from app.config import get_settings


class KnowledgeExtractor:
    def __init__(self) -> None:
        settings = get_settings()
        self.llm = ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            google_api_key=settings.google_api_key,
            temperature=0,
        )

    async def extract(self, full_text_sample: str) -> dict:
        prompt = (
            "Extract structured metadata from this research paper excerpt. "
            "Return JSON with keys: authors (list), models (list), datasets (list), "
            "metrics (list), methods (list), results (list), limitations (list).\n\n"
            f"{full_text_sample[:12000]}"
        )
        resp = await self.llm.ainvoke(
            [SystemMessage(content="JSON only."), HumanMessage(content=prompt)]
        )
        text = resp.content.strip()
        if "```" in text:
            text = text.split("```")[1].replace("json", "", 1)
        return json.loads(text)
