import { AuthGuard } from "@/components/auth-guard";
import { DashboardShell } from "@/components/layout/dashboard-shell";
import { ErrorBoundary } from "@/components/error-boundary";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthGuard>
      <DashboardShell>
        <ErrorBoundary>{children}</ErrorBoundary>
      </DashboardShell>
    </AuthGuard>
  );
}
