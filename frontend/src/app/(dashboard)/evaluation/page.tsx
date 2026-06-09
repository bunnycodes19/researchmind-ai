"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function EvaluationPage() {
  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold">RAG Evaluation</h1>
      <p className="mt-1 text-zinc-500">
        RAGAS metrics (relevance, faithfulness, context precision/recall) are computed automatically after each answer.
      </p>

      <div className="mt-8 grid gap-4 md:grid-cols-2">
        {[
          { title: "Answer Relevance", desc: "How well the answer addresses the question (RAGAS answer_relevancy)." },
          { title: "Faithfulness", desc: "Whether claims are supported by retrieved context." },
          { title: "Context Precision", desc: "Quality of retrieved chunks ranking." },
          { title: "Context Recall", desc: "Coverage of information needed to answer." },
        ].map((m) => (
          <Card key={m.title}>
            <CardHeader>
              <CardTitle className="text-base">{m.title}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-zinc-500">{m.desc}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <p className="mt-8 text-sm text-zinc-600">
        Per-message scores: GET /api/v1/dashboard/evaluations/{"{message_id}"} after chatting in Workspace.
      </p>
    </div>
  );
}
