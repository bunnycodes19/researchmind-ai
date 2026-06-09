"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { Send, AlertTriangle } from "lucide-react";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useUIStore } from "@/stores/ui-store";
import { Skeleton } from "@/components/ui/skeleton";

interface Message {
  id: string;
  role: string;
  content: string;
  citations?: { page_number: number; excerpt: string; paper_title: string }[];
  confidence?: number;
}

export function ChatPanel({ sessionId }: { sessionId: string }) {
  const [input, setInput] = useState("");
  const explainMode = useUIStore((s) => s.explainMode);
  const selectedPaperIds = useUIStore((s) => s.selectedPaperIds);
  const qc = useQueryClient();

  const { data: messages, isLoading } = useQuery({
    queryKey: ["messages", sessionId],
    queryFn: () => api<Message[]>(`/api/v1/chat/sessions/${sessionId}/messages`),
    enabled: !!sessionId,
  });

  const send = useMutation({
    mutationFn: (content: string) =>
      api<{ message: Message; low_confidence_warning: boolean }>(
        `/api/v1/chat/sessions/${sessionId}/messages`,
        {
          method: "POST",
          json: { content, mode: explainMode, paper_ids: selectedPaperIds.length ? selectedPaperIds : null },
        },
      ),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["messages", sessionId] }),
  });

  return (
    <div className="flex h-full flex-col">
      <div className="flex-1 space-y-4 overflow-y-auto p-6">
        {isLoading && (
          <>
            <Skeleton className="h-16 w-3/4" />
            <Skeleton className="ml-auto h-12 w-1/2" />
          </>
        )}
        {messages?.map((m) => (
          <motion.div
            key={m.id}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            className={`max-w-3xl rounded-xl px-4 py-3 ${
              m.role === "user" ? "ml-auto bg-violet-600/30" : "bg-zinc-900 border border-zinc-800"
            }`}
          >
            <p className="whitespace-pre-wrap text-sm leading-relaxed">{m.content}</p>
            {m.role === "assistant" && m.confidence != null && (
              <p className="mt-2 text-xs text-zinc-500">Confidence: {(m.confidence * 100).toFixed(0)}%</p>
            )}
            {m.citations?.length ? (
              <div className="mt-3 space-y-1 border-t border-zinc-800 pt-2">
                {m.citations.map((c, i) => (
                  <p key={i} className="text-xs text-zinc-500">
                    [{c.paper_title} p.{c.page_number}] {c.excerpt?.slice(0, 120)}…
                  </p>
                ))}
              </div>
            ) : null}
          </motion.div>
        ))}
        {send.data?.low_confidence_warning && (
          <div className="flex items-center gap-2 rounded-lg border border-amber-800/50 bg-amber-950/30 p-3 text-amber-200 text-sm">
            <AlertTriangle className="h-4 w-4 shrink-0" />
            Low confidence — verify against the source PDF.
          </div>
        )}
      </div>
      <form
        className="flex gap-2 border-t border-zinc-800 p-4"
        onSubmit={(e) => {
          e.preventDefault();
          if (!input.trim()) return;
          send.mutate(input);
          setInput("");
        }}
      >
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about methodology, results, limitations…"
          disabled={send.isPending}
        />
        <Button type="submit" disabled={send.isPending}>
          <Send className="h-4 w-4" />
        </Button>
      </form>
    </div>
  );
}
