from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.config import get_settings


class EmbeddingService:
    def __init__(self) -> None:
        settings = get_settings()
        if not settings.google_api_key:
            raise ValueError("GOOGLE_API_KEY is required for embeddings")
        self._client = GoogleGenerativeAIEmbeddings(
            model=settings.embedding_model,
            google_api_key=settings.google_api_key,
        )

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return await self._client.aembed_documents(texts)

    async def embed_query(self, text: str) -> list[float]:
        return await self._client.aembed_query(text)

    @property
    def dimension(self) -> int:
        return 768
