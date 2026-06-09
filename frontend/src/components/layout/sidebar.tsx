"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BarChart3,
  BookOpen,
  FileText,
  GitCompare,
  LayoutDashboard,
  LogOut,
  MessageSquare,
  Settings,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/stores/auth-store";
import { api, clearTokens } from "@/lib/api";
import { useRouter } from "next/navigation";

const links = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/papers", label: "Papers", icon: FileText },
  { href: "/workspace", label: "Workspace", icon: MessageSquare },
  { href: "/compare", label: "Compare", icon: GitCompare },
  { href: "/study", label: "Study", icon: BookOpen },
  { href: "/evaluation", label: "RAG Eval", icon: BarChart3 },
  { href: "/settings", label: "Settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);

  const handleLogout = async () => {
    try {
      await api("/api/v1/auth/logout", { method: "POST" });
    } catch {
      /* ignore */
    }
    clearTokens();
    logout();
    router.push("/login");
  };

  return (
    <aside className="flex h-screen w-64 flex-col border-r border-zinc-800 bg-zinc-950/90">
      <div className="border-b border-zinc-800 p-6">
        <Link href="/dashboard" className="flex items-center gap-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-violet-600 font-bold text-white">
            R
          </div>
          <div>
            <p className="font-semibold text-zinc-100">ResearchMind</p>
            <p className="text-xs text-zinc-500">AI Research Assistant</p>
          </div>
        </Link>
      </div>
      <nav className="flex-1 space-y-1 p-4">
        {links.map(({ href, label, icon: Icon }) => (
          <Link
            key={href}
            href={href}
            className={cn(
              "flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors",
              pathname.startsWith(href)
                ? "bg-violet-600/20 text-violet-300"
                : "text-zinc-400 hover:bg-zinc-900 hover:text-zinc-200",
            )}
          >
            <Icon className="h-4 w-4" />
            {label}
          </Link>
        ))}
      </nav>
      <div className="border-t border-zinc-800 p-4">
        <p className="truncate text-sm text-zinc-300">{user?.full_name}</p>
        <p className="truncate text-xs text-zinc-500">{user?.email}</p>
        <button
          onClick={handleLogout}
          className="mt-3 flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm text-zinc-400 hover:bg-zinc-900 hover:text-red-400"
        >
          <LogOut className="h-4 w-4" />
          Log out
        </button>
      </div>
    </aside>
  );
}
