"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { api } from "@/lib/api";
import { ChatPanel } from "@/components/chat/chat-panel";
import { Button } from "@/components/ui/button";
import { useUIStore } from "@/stores/ui-store";

interface Session {
  id: string;
  title: string;
}

export default function WorkspacePage() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const explainMode = useUIStore((s) => s.explainMode);
  const setExplainMode = useUIStore((s) => s.setExplainMode);
  const selectedPaperIds = useUIStore((s) => s.selectedPaperIds);
  const qc = useQueryClient();

  const { data: sessions } = useQuery({
    queryKey: ["sessions"],
    queryFn: () => api<Session[]>("/api/v1/chat/sessions"),
  });

  const createSession = useMutation({
    mutationFn: () =>
      api<Session>("/api/v1/chat/sessions", {
        method: "POST",
        json: {
          title: "Research chat",
          paper_ids: selectedPaperIds.length ? selectedPaperIds : null,
        },
      }),
    onSuccess: (s) => {
      setSessionId(s.id);
      qc.invalidateQueries({ queryKey: ["sessions"] });
    },
  });

  const active = sessionId || sessions?.[0]?.id;

  return (
    <div className="flex h-screen flex-col">
      <div className="flex items-center justify-between border-b border-zinc-800 px-6 py-4">
        <div>
          <h1 className="text-xl font-bold">Workspace</h1>
          <p className="text-sm text-zinc-500">Ask questions with citation-backed RAG</p>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={explainMode}
            onChange={(e) => setExplainMode(e.target.value as "simple" | "intermediate" | "expert")}
            className="rounded-lg border border-zinc-700 bg-zinc-900 px-3 py-2 text-sm"
          >
            <option value="simple">ELI5</option>
            <option value="intermediate">Intermediate</option>
            <option value="expert">Expert</option>
          </select>
          <Button variant="secondary" onClick={() => createSession.mutate()}>
            New chat
          </Button>
        </div>
      </div>
      {active ? (
        <ChatPanel sessionId={active} />
      ) : (
        <div className="flex flex-1 items-center justify-center text-zinc-500">
          <Button onClick={() => createSession.mutate()}>Start a conversation</Button>
        </div>
      )}
    </div>
  );
}
