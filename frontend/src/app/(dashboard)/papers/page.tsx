"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Trash2 } from "lucide-react";
import { api } from "@/lib/api";
import { UploadZone } from "@/components/papers/upload-zone";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useUIStore } from "@/stores/ui-store";
import { toast } from "sonner";

interface Paper {
  id: string;
  title: string;
  filename: string;
  status: string;
  page_count: number;
  created_at: string;
}

export default function PapersPage() {
  const qc = useQueryClient();
  const togglePaper = useUIStore((s) => s.togglePaperSelection);
  const selected = useUIStore((s) => s.selectedPaperIds);

  const { data, isLoading } = useQuery({
    queryKey: ["papers"],
    queryFn: () => api<{ items: Paper[]; total: number }>("/api/v1/papers"),
  });

  const remove = useMutation({
    mutationFn: (id: string) => api(`/api/v1/papers/${id}`, { method: "DELETE" }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["papers"] });
      toast.success("Paper deleted");
    },
  });

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold">Papers</h1>
      <p className="mt-1 text-zinc-500">Upload and manage your research library</p>

      <div className="mt-8">
        <UploadZone />
      </div>

      <div className="mt-8 space-y-4">
        {isLoading &&
          Array.from({ length: 3 }).map((_, i) => <Skeleton key={i} className="h-20 w-full rounded-xl" />)}
        {data?.items.map((paper) => (
          <Card key={paper.id} className={selected.includes(paper.id) ? "ring-1 ring-violet-500" : ""}>
            <CardContent className="flex items-center justify-between p-4">
              <div className="flex items-center gap-4">
                <input
                  type="checkbox"
                  checked={selected.includes(paper.id)}
                  onChange={() => togglePaper(paper.id)}
                  className="rounded border-zinc-600"
                />
                <div>
                  <p className="font-medium">{paper.title}</p>
                  <p className="text-xs text-zinc-500">
                    {paper.filename} · {paper.page_count} pages ·{" "}
                    <span
                      className={
                        paper.status === "ready"
                          ? "text-emerald-400"
                          : paper.status === "failed"
                            ? "text-red-400"
                            : "text-amber-400"
                      }
                    >
                      {paper.status}
                    </span>
                  </p>
                </div>
              </div>
              <Button variant="ghost" size="sm" onClick={() => remove.mutate(paper.id)}>
                <Trash2 className="h-4 w-4 text-red-400" />
              </Button>
            </CardContent>
          </Card>
        ))}
        {!isLoading && !data?.items.length && (
          <Card>
            <CardHeader>
              <CardTitle className="text-base text-zinc-500">No papers yet</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-zinc-600">Upload your first PDF above to begin.</p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
