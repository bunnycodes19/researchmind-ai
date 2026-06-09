from uuid import UUID

from ragas import evaluate
from ragas.metrics import (
    answer_relevancy,
    context_precision,
    context_recall,
    faithfulness,
)
from datasets import Dataset

from app.config import get_settings


class RAGEvaluationService:
    async def evaluate_turn(
        self,
        question: str,
        answer: str,
        contexts: list[str],
    ) -> dict[str, float | None]:
        settings = get_settings()
        if not settings.google_api_key:
            return {
                "relevance": None,
                "faithfulness": None,
                "context_precision": None,
                "context_recall": None,
            }

        try:
            ds = Dataset.from_dict(
                {
                    "question": [question],
                    "answer": [answer],
                    "contexts": [contexts],
                }
            )
            result = evaluate(
                ds,
                metrics=[answer_relevancy, faithfulness, context_precision, context_recall],
            )
            df = result.to_pandas()
            row = df.iloc[0]
            return {
                "relevance": float(row.get("answer_relevancy", 0) or 0),
                "faithfulness": float(row.get("faithfulness", 0) or 0),
                "context_precision": float(row.get("context_precision", 0) or 0),
                "context_recall": float(row.get("context_recall", 0) or 0),
            }
        except Exception:
            return {
                "relevance": None,
                "faithfulness": None,
                "context_precision": None,
                "context_recall": None,
            }
