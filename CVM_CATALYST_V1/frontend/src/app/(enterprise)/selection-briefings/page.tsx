import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";

export default function SelectionBriefingsPage() {
  return (
    <div className="grid gap-4 xl:grid-cols-3">
      <Card className="xl:col-span-2">
        <CardHeader>
          <CardTitle>Selection Briefings</CardTitle>
          <CardDescription>Capture campaign intent, constraints, and measurement hypotheses in one briefing artifact.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <Input placeholder="Briefing title" defaultValue="Q4 Retention High-Value Segment" />
          <Textarea
            rows={8}
            defaultValue="Objective: reduce churn by 1.4 points among high-value postpaid segments.\nGuardrails: no more than 2 outbound touches per customer.\nKPI: incremental margin uplift."
          />
          <div className="flex flex-wrap gap-2">
            <Button>Save Briefing</Button>
            <Button variant="secondary">Route To Audience Designer</Button>
          </div>
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>Briefing Intelligence</CardTitle>
          <CardDescription>Policy and quality checks from briefing intake agents.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-2 text-sm">
          <p>Coverage score: 92/100</p>
          <p>Missing field: legal basis for cross-channel personalization.</p>
          <p>Recommended next action: validate consent logic before approval routing.</p>
        </CardContent>
      </Card>
    </div>
  );
}
