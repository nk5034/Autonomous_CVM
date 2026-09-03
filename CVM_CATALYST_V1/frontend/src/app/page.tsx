import Link from "next/link";

import { enterpriseNav } from "@/lib/enterprise-nav";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function HomePage() {
  return (
    <main className="mx-auto min-h-screen max-w-6xl px-4 py-10 md:px-8">
      <section className="rounded-3xl border border-border bg-white/90 p-6 shadow-enterprise md:p-8">
        <p className="text-xs uppercase tracking-[0.25em] text-muted-foreground">Vodafone Enterprise</p>
        <h1 className="mt-2 text-4xl font-semibold tracking-tight md:text-5xl">CVM Catalyst Frontend</h1>
        <p className="mt-3 max-w-2xl text-muted-foreground">
          Phase 11 interface suite for campaign design, governance, experimentation, simulation, and reporting.
        </p>
        <div className="mt-5">
          <Button asChild>
            <Link href="/dashboard">Open Dashboard</Link>
          </Button>
        </div>
      </section>

      <section className="mt-6 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
        {enterpriseNav.map((item) => {
          const Icon = item.icon;
          return (
            <Card key={item.href} className="transition-transform hover:-translate-y-1">
              <CardHeader>
                <div className="flex items-center gap-2">
                  <Icon className="h-4 w-4 text-vf-red" />
                  <CardTitle className="text-base">{item.title}</CardTitle>
                </div>
                <CardDescription>{item.description}</CardDescription>
              </CardHeader>
              <CardContent>
                <Link href={item.href} className="text-sm font-semibold text-vf-red hover:underline">
                  Enter workspace
                </Link>
              </CardContent>
            </Card>
          );
        })}
      </section>
    </main>
  );
}
