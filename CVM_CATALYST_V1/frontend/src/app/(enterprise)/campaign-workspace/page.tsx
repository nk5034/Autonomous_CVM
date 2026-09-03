import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

const workstreams = [
  { name: "Retention Pulse Q4", owner: "CVM Squad A", status: "In Progress", readiness: "83%" },
  { name: "SME Upsell Sprint", owner: "Commercial Ops", status: "At Risk", readiness: "64%" },
  { name: "Roaming Rescue", owner: "Digital Sales", status: "Ready", readiness: "95%" },
];

export default function CampaignWorkspacePage() {
  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Campaign Workspace</CardTitle>
          <CardDescription>Organize planning pods, stage-gates, and dependencies across campaign waves.</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-2">
          <Button>New Campaign Wave</Button>
          <Button variant="secondary">Import Planning Sheet</Button>
          <Button variant="ghost">Sync From Orchestration</Button>
        </CardContent>
      </Card>

      <section className="grid gap-3 lg:grid-cols-3">
        {workstreams.map((stream) => (
          <Card key={stream.name}>
            <CardHeader>
              <div className="flex items-center justify-between gap-2">
                <CardTitle className="text-base">{stream.name}</CardTitle>
                <Badge variant={stream.status === "At Risk" ? "warning" : "success"}>{stream.status}</Badge>
              </div>
              <CardDescription>{stream.owner}</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">Readiness: {stream.readiness}</p>
            </CardContent>
          </Card>
        ))}
      </section>
    </div>
  );
}
