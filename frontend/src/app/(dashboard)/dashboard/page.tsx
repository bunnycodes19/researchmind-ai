"use client";

import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { FileText, HardDrive, HelpCircle, Layers } from "lucide-react";
import { api } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

interface Stats {
  total_papers: number;
  total_chunks: number;
  questions_asked: number;
  papers_processing: number;
  storage_usage_bytes: number;
  recent_activity: { action: string; created_at: string }[];
}

export default function DashboardPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["dashboard"],
    queryFn: () => api<Stats>("/api/v1/dashboard/stats"),
  });

  const cards = [
    { label: "Papers", value: data?.total_papers, icon: FileText },
    { label: "Chunks indexed", value: data?.total_chunks, icon: Layers },
    { label: "Questions asked", value: data?.questions_asked, icon: HelpCircle },
    {
      label: "Storage",
      value: data ? `${(data.storage_usage_bytes / 1024 / 1024).toFixed(1)} MB` : undefined,
      icon: HardDrive,
    },
  ];

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold">Dashboard</h1>
      <p className="mt-1 text-zinc-500">Overview of your research workspace</p>

      <div className="mt-8 grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {cards.map((c, i) => (
          <motion.div key={c.label} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }}>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-zinc-400">{c.label}</CardTitle>
                <c.icon className="h-4 w-4 text-violet-400" />
              </CardHeader>
              <CardContent>
                {isLoading ? <Skeleton className="h-8 w-16" /> : <p className="text-3xl font-bold">{c.value ?? 0}</p>}
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      {data?.papers_processing ? (
        <p className="mt-6 text-sm text-amber-400">{data.papers_processing} paper(s) processing…</p>
      ) : null}

      <Card className="mt-8">
        <CardHeader>
          <CardTitle>Recent activity</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading && <Skeleton className="h-24 w-full" />}
          {!isLoading && !data?.recent_activity?.length && (
            <p className="text-sm text-zinc-500">No activity yet. Upload a paper to get started.</p>
          )}
          <ul className="space-y-2">
            {data?.recent_activity?.map((a, i) => (
              <li key={i} className="flex justify-between text-sm text-zinc-400">
                <span>{a.action}</span>
                <span>{new Date(a.created_at).toLocaleString()}</span>
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}
