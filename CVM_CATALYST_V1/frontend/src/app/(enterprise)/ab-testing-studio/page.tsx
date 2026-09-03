"use client";

import { useState } from "react";
import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { runEnterpriseABPreview } from "@/lib/api/enterprise";

function pct(value: number): string {
  return `${(value * 100).toFixed(2)}%`;
}

export default function ABTestingStudioPage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [headline, setHeadline] = useState(
    "Run a live preview to pull latest variant uplift and confidence from backend services.",
  );

  const onRunPreview = async () => {
    setLoading(true);
    setError("");
    const result = await runEnterpriseABPreview();
    if (!result) {
      setError("A/B preview failed. Verify backend availability.");
      setLoading(false);
      return;
    }

    const lead = result.variant_performance[0];
    if (!lead) {
      setHeadline("No variant performance data returned.");
    } else {
      setHeadline(
        `${result.experiment_name}: ${lead.name} at ${pct(lead.confidence)} confidence with ${pct(lead.lift)} relative lift.`,
      );
    }
    setLoading(false);
  };

  return (
    <div className="grid gap-4 xl:grid-cols-3">
      <Card className="xl:col-span-2">
        <CardHeader>
          <CardTitle>A/B Testing Studio</CardTitle>
          <CardDescription>Compare treatment variants and confidence with enterprise decision thresholds.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="rounded-xl border border-border bg-muted/40 p-3 text-sm">{headline}</div>
          {error ? <p className="text-sm text-red-600">{error}</p> : null}
          <Button asChild>
            <Link href="/campaigns/ab-testing">Open Experiment Workbench</Link>
          </Button>
          <Button variant="secondary" onClick={onRunPreview} disabled={loading}>
            {loading ? "Running..." : "Run Live AB Preview"}
          </Button>
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>Policy Gate</CardTitle>
          <CardDescription>Auto-checks before full rollout</CardDescription>
        </CardHeader>
        <CardContent className="space-y-2">
          <div className="flex items-center justify-between"><span className="text-sm">Minimum sample size</span><Badge variant="success">Pass</Badge></div>
          <div className="flex items-center justify-between"><span className="text-sm">Bias check</span><Badge variant="success">Pass</Badge></div>
          <div className="flex items-center justify-between"><span className="text-sm">Holdout protection</span><Badge variant="warning">Review</Badge></div>
        </CardContent>
      </Card>
    </div>
  );
}
