"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useUIStore } from "@/stores/ui-store";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function StudyPage() {
  const selected = useUIStore((s) => s.selectedPaperIds);
  const paperId = selected[0];
  const [result, setResult] = useState<Record<string, unknown> | null>(null);

  const summary = useMutation({
    mutationFn: () =>
      api<{ content: Record<string, unknown> }>("/api/v1/study/summary", {
        method: "POST",
        json: { paper_id: paperId },
      }),
    onSuccess: (d) => setResult(d.content),
  });

  const flashcards = useMutation({
    mutationFn: () =>
      api<{ content: Record<string, unknown> }>("/api/v1/study/generate", {
        method: "POST",
        json: { paper_id: paperId, artifact_type: "flashcards" },
      }),
    onSuccess: (d) => setResult(d.content),
  });

  const literature = useMutation({
    mutationFn: () =>
      api<{ content: Record<string, unknown> }>("/api/v1/study/literature-review", {
        method: "POST",
        json: { paper_ids: selected },
      }),
    onSuccess: (d) => setResult(d.content),
  });

  if (!paperId) {
    return (
      <div className="p-8">
        <h1 className="text-2xl font-bold">Study assistant</h1>
        <p className="mt-4 text-zinc-500">Select at least one ready paper on the Papers page.</p>
      </div>
    );
  }

  const busy = summary.isPending || flashcards.isPending || literature.isPending;

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold">Study assistant</h1>
      <p className="mt-1 text-zinc-500">Summaries, flashcards, quizzes, and literature reviews</p>

      <div className="mt-6 flex flex-wrap gap-3">
        <Button onClick={() => summary.mutate()} disabled={busy}>
          Executive summary
        </Button>
        <Button variant="secondary" onClick={() => flashcards.mutate()} disabled={busy}>
          Flashcards
        </Button>
        <Button variant="secondary" onClick={() => literature.mutate()} disabled={busy || selected.length < 1}>
          Literature review
        </Button>
      </div>

      {result && (
        <Card className="mt-8">
          <CardHeader>
            <CardTitle>Generated content</CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="max-h-[60vh] overflow-auto whitespace-pre-wrap text-sm text-zinc-300">
              {JSON.stringify(result, null, 2)}
            </pre>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
