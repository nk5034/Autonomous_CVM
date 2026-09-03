import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getDashboardSnapshot } from "@/lib/api/enterprise";
import { attentionFeed } from "@/lib/enterprise-nav";
import { KpiGrid, StageProgress, StreamPanel } from "@/components/common/enterprise-blocks";

export default async function DashboardPage() {
  const snapshot = await getDashboardSnapshot();
  const heroMetrics = [
    { label: "Active Campaigns", value: snapshot.activeCampaigns, delta: "+12.4%" },
    { label: "Projected Reach", value: snapshot.projectedReach, delta: "Live" },
    { label: "AB Confidence Target", value: snapshot.confidenceTarget, delta: "Live" },
    { label: "Briefing Versions", value: snapshot.briefingVersions, delta: "Live" },
  ];

  return (
    <div className="space-y-4">
      <KpiGrid items={heroMetrics} />

      <section className="grid gap-4 xl:grid-cols-3">
        <div className="xl:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Portfolio Performance Lattice</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-56 rounded-2xl border border-border bg-gradient-to-r from-vf-red-soft via-white to-vf-steel/20 p-4">
                <div className="grid h-full grid-cols-3 grid-rows-3 gap-2">
                  {Array.from({ length: 9 }).map((_, idx) => (
                    <div key={idx} className="rounded-lg border border-border/70 bg-white/70 p-2 text-xs">
                      Cluster {idx + 1}
                      <div className="mt-2 h-1 w-full origin-left rounded-full bg-vf-red/40 animate-pulse-line" />
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
        <div className="space-y-4">
          <StageProgress title="Orchestration Health" subtitle="Node completion across active workflows" progress={84} />
          <StageProgress title="Data Readiness" subtitle="Metadata and synthetic assets validated" progress={91} />
        </div>
      </section>

      <StreamPanel title="Decision Feed" items={attentionFeed} />
    </div>
  );
}
