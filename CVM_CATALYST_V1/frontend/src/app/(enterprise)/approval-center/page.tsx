import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { getApprovalQueueSnapshot } from "@/lib/api/enterprise";

export default async function ApprovalCenterPage() {
  const queue = await getApprovalQueueSnapshot();

  return (
    <Card>
      <CardHeader>
        <CardTitle>Approval Center</CardTitle>
        <CardDescription>Multi-stage governance queue for campaign artifacts and deployment decisions.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        {queue.map((entry) => (
          <article key={entry.item} className="rounded-xl border border-border p-3">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <h3 className="font-medium">{entry.item}</h3>
              <Badge variant={entry.risk === "High" ? "warning" : "neutral"}>{entry.risk} Risk</Badge>
            </div>
            <p className="mt-1 text-sm text-muted-foreground">Owner: {entry.owner}</p>
          </article>
        ))}
        <div className="flex flex-wrap gap-2">
          <Button>Approve Selected</Button>
          <Button variant="secondary">Request Rework</Button>
        </div>
      </CardContent>
    </Card>
  );
}
