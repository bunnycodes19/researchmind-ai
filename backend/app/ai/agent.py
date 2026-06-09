from typing import TypedDict
from uuid import UUID

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, StateGraph

from app.ai.retriever import RetrieverService
from app.config import get_settings


class AgentState(TypedDict):
    question: str
    paper_ids: list[str]
    user_id: str
    evidence: list[dict]
    comparison_notes: str
    report: str


async def search_evidence(state: AgentState) -> AgentState:
    retriever = RetrieverService(UUID(state["user_id"]))
    hits = await retriever.retrieve(state["question"], [UUID(p) for p in state["paper_ids"]])
    reranked = await retriever.rerank(state["question"], hits)
    state["evidence"] = reranked
    return state


async def compare_findings(state: AgentState) -> AgentState:
    settings = get_settings()
    llm = ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        google_api_key=settings.google_api_key,
        temperature=0.2,
    )
    ctx = "\n".join(e["metadata"].get("content", "")[:300] for e in state["evidence"][:8])
    resp = await llm.ainvoke(
        [
            SystemMessage(content="Compare findings across papers briefly."),
            HumanMessage(content=f"Question: {state['question']}\n\nEvidence:\n{ctx}"),
        ]
    )
    state["comparison_notes"] = resp.content
    return state


async def generate_report(state: AgentState) -> AgentState:
    settings = get_settings()
    llm = ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        google_api_key=settings.google_api_key,
        temperature=0.2,
    )
    resp = await llm.ainvoke(
        [
            SystemMessage(content="Write a structured research report with citations [Source N]."),
            HumanMessage(
                content=(
                    f"Question: {state['question']}\n"
                    f"Comparison: {state['comparison_notes']}\n"
                    f"Evidence count: {len(state['evidence'])}"
                )
            ),
        ]
    )
    state["report"] = resp.content
    return state


def build_research_agent():
    graph = StateGraph(AgentState)
    graph.add_node("search", search_evidence)
    graph.add_node("compare", compare_findings)
    graph.add_node("write_report", generate_report)
    graph.set_entry_point("search")
    graph.add_edge("search", "compare")
    graph.add_edge("compare", "write_report")
    graph.add_edge("write_report", END)
    return graph.compile()


async def run_research_agent(user_id: UUID, question: str, paper_ids: list[UUID]) -> str:
    agent = build_research_agent()
    result = await agent.ainvoke(
        {
            "question": question,
            "paper_ids": [str(p) for p in paper_ids],
            "user_id": str(user_id),
            "evidence": [],
            "comparison_notes": "",
            "report": "",
        }
    )
    return result["report"]
