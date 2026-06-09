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
        import asyncio
        batch_size = 16
        all_embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            embeddings = await self._client.aembed_documents(batch)
            all_embeddings.extend(embeddings)
            if i + batch_size < len(texts):
                await asyncio.sleep(1.0)  # Pause for 1 second between batches to avoid 429 Quota limits
        return all_embeddings

    async def embed_query(self, text: str) -> list[float]:
        return await self._client.aembed_query(text)

    @property
    def dimension(self) -> int:
        return 768
