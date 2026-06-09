from pydantic import BaseModel


class DashboardStats(BaseModel):
    total_papers: int
    total_chunks: int
    questions_asked: int
    papers_processing: int
    storage_usage_bytes: int
    recent_activity: list[dict]


class EvaluationResponse(BaseModel):
    message_id: str
    relevance: float | None
    faithfulness: float | None
    context_precision: float | None
    context_recall: float | None
