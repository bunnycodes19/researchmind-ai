"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useUIStore } from "@/stores/ui-store";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function ComparePage() {
  const selected = useUIStore((s) => s.selectedPaperIds);
  const [question, setQuestion] = useState("Compare methodology, datasets, and results across these papers.");

  const compare = useMutation({
    mutationFn: () =>
      api<{ comparison_table: Record<string, unknown>[]; narrative: string }>("/api/v1/papers/compare", {
        method: "POST",
        json: { paper_ids: selected, question },
      }),
  });

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold">Compare papers</h1>
      <p className="mt-1 text-zinc-500">
        Select 2+ papers on the Papers page, then run multi-paper analysis (LangGraph agent).
      </p>

      <div className="mt-6 max-w-2xl space-y-4">
        <p className="text-sm text-zinc-400">{selected.length} paper(s) selected</p>
        <Input value={question} onChange={(e) => setQuestion(e.target.value)} />
        <Button disabled={selected.length < 2 || compare.isPending} onClick={() => compare.mutate()}>
          {compare.isPending ? "Analyzing…" : "Compare"}
        </Button>
      </div>

      {compare.data && (
        <div className="mt-8 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Analysis</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="whitespace-pre-wrap text-sm leading-relaxed">{compare.data.narrative}</p>
            </CardContent>
          </Card>
          {compare.data.comparison_table?.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Comparison table</CardTitle>
              </CardHeader>
              <CardContent>
                <pre className="overflow-auto text-xs text-zinc-400">
                  {JSON.stringify(compare.data.comparison_table, null, 2)}
                </pre>
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  );
}
