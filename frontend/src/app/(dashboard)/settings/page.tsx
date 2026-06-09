"use client";

import { useAuthStore } from "@/stores/auth-store";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { useState } from "react";
import { api } from "@/lib/api";
import { toast } from "sonner";

export default function SettingsPage() {
  const user = useAuthStore((s) => s.user);
  const setUser = useAuthStore((s) => s.setUser);
  const [name, setName] = useState(user?.full_name || "");

  const save = async () => {
    try {
      const updated = await api<{ full_name: string }>("/api/v1/auth/me", {
        method: "PATCH",
        json: { full_name: name },
      });
      if (user) setUser({ ...user, full_name: updated.full_name });
      toast.success("Profile updated");
    } catch {
      toast.error("Update failed");
    }
  };

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold">Settings</h1>
      <Card className="mt-8 max-w-lg">
        <CardHeader>
          <CardTitle>Profile</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="text-xs text-zinc-500">Email</label>
            <p className="text-sm">{user?.email}</p>
          </div>
          <div>
            <label className="text-xs text-zinc-500">Full name</label>
            <Input value={name} onChange={(e) => setName(e.target.value)} />
          </div>
          <Button onClick={save}>Save</Button>
        </CardContent>
      </Card>
    </div>
  );
}
