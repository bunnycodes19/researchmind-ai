"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, BookOpen, Brain, Search, Shield } from "lucide-react";
import { Button } from "@/components/ui/button";

const features = [
  { icon: Search, title: "Semantic Search", desc: "FAISS-powered retrieval across your paper library." },
  { icon: Brain, title: "RAG Q&A", desc: "Citation-backed answers with hallucination confidence scores." },
  { icon: BookOpen, title: "Study Tools", desc: "Summaries, flashcards, literature reviews, and comparisons." },
  { icon: Shield, title: "RAGAS Eval", desc: "Measure faithfulness, relevance, and context quality." },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-zinc-950">
      <header className="mx-auto flex max-w-6xl items-center justify-between px-6 py-6">
        <div className="flex items-center gap-2">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-violet-600 font-bold">R</div>
          <span className="text-xl font-semibold">ResearchMind AI</span>
        </div>
        <div className="flex gap-3">
          <Link href="/login">
            <Button variant="ghost">Log in</Button>
          </Link>
          <Link href="/signup">
            <Button>Get started</Button>
          </Link>
        </div>
      </header>

      <section className="mx-auto max-w-6xl px-6 py-24 text-center">
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-5xl font-bold tracking-tight md:text-6xl"
        >
          Understand research papers
          <span className="block bg-gradient-to-r from-violet-400 to-fuchsia-400 bg-clip-text text-transparent">
            at startup speed
          </span>
        </motion.h1>
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="mx-auto mt-6 max-w-2xl text-lg text-zinc-400"
        >
          Upload PDFs, ask questions with citations, generate literature reviews, and compare papers — powered by
          LangChain, Gemini, and FAISS.
        </motion.p>
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }} className="mt-10">
          <Link href="/signup">
            <Button size="lg" className="gap-2">
              Start free <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
        </motion.div>
      </section>

      <section className="mx-auto grid max-w-6xl gap-6 px-6 pb-24 md:grid-cols-2 lg:grid-cols-4">
        {features.map((f, i) => (
          <motion.div
            key={f.title}
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 * i }}
            className="rounded-xl border border-zinc-800 bg-zinc-900/50 p-6"
          >
            <f.icon className="mb-4 h-8 w-8 text-violet-400" />
            <h3 className="font-semibold">{f.title}</h3>
            <p className="mt-2 text-sm text-zinc-500">{f.desc}</p>
          </motion.div>
        ))}
      </section>
    </div>
  );
}
