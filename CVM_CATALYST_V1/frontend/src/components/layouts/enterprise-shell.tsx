"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { enterpriseNav } from "@/lib/enterprise-nav";
import { cn } from "@/lib/utils/cn";
import { Badge } from "@/components/ui/badge";

export function EnterpriseShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="pointer-events-none fixed inset-0 -z-10 bg-grid" />
      <div className="mx-auto flex w-full max-w-[1600px] gap-4 px-3 py-4 md:px-5 md:py-6">
        <aside className="hidden w-[300px] shrink-0 rounded-2xl border border-border/70 bg-white/95 p-4 shadow-enterprise lg:block">
          <div className="mb-4 rounded-xl bg-vf-red px-4 py-3 text-white">
            <p className="text-xs uppercase tracking-[0.2em] text-white/80">Vodafone Enterprise</p>
            <h1 className="text-xl font-semibold">CVM Catalyst</h1>
          </div>

          <div className="mb-5 flex items-center justify-between">
            <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Control Plane</p>
            <Badge variant="neutral">Phase 11</Badge>
          </div>

          <nav className="space-y-1">
            {enterpriseNav.map((item) => {
              const active = pathname === item.href;
              const Icon = item.icon;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "flex items-center gap-3 rounded-xl border px-3 py-2 transition-all",
                    active
                      ? "border-vf-red/30 bg-vf-red-soft text-vf-red"
                      : "border-transparent text-foreground hover:border-border hover:bg-muted",
                  )}
                >
                  <Icon className="h-4 w-4" />
                  <div>
                    <p className="text-sm font-medium">{item.title}</p>
                    <p className="text-xs text-muted-foreground">{item.description}</p>
                  </div>
                </Link>
              );
            })}
          </nav>
        </aside>

        <div className="flex min-h-[90vh] flex-1 flex-col overflow-hidden rounded-2xl border border-border/70 bg-white/95 shadow-enterprise">
          <header className="border-b border-border px-4 py-4 md:px-6">
            <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
              <div>
                <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">CVM Operating System</p>
                <h2 className="text-2xl font-semibold tracking-tight">Enterprise Frontend Workspace</h2>
              </div>
              <div className="flex gap-2 overflow-auto pb-1 lg:hidden">
                {enterpriseNav.map((item) => (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={cn(
                      "whitespace-nowrap rounded-full border px-3 py-1 text-xs",
                      pathname === item.href ? "border-vf-red bg-vf-red-soft text-vf-red" : "border-border",
                    )}
                  >
                    {item.title}
                  </Link>
                ))}
              </div>
            </div>
          </header>
          <main className="flex-1 p-4 md:p-6">{children}</main>
        </div>
      </div>
    </div>
  );
}
