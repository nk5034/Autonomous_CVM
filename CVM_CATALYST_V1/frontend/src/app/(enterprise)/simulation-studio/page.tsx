"use client";

import { useState } from "react";
import Link from "next/link";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { runEnterpriseSimulationPreview } from "@/lib/api/enterprise";

function asPercent(value: number): string {
  return `${(value * 100).toFixed(2)}%`;
}

export default function SimulationStudioPage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [forecasts, setForecasts] = useState<Array<{ metric: string; value: string }>>([
    { metric: "Projected Reach", value: "n/a" },
    { metric: "Expected Response", value: "n/a" },
    { metric: "Expected ROI", value: "n/a" },
  ]);

  const onRunPreview = async () => {
    setLoading(true);
    setError("");
    const result = await runEnterpriseSimulationPreview();
    if (!result) {
      setError("Simulation preview failed. Verify backend availability.");
      setLoading(false);
      return;
    }

    setForecasts([
      { metric: "Projected Reach", value: result.expected_audience.target_audience.toLocaleString() },
      { metric: "Expected Response", value: asPercent(result.response_forecast.effective_response_rate) },
      { metric: "Expected ROI", value: `${result.roi_forecast.roi.toFixed(2)}x` },
    ]);
    setLoading(false);
  };

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Simulation Studio</CardTitle>
          <CardDescription>Scenario-level what-if modeling connected to campaign simulation services.</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-2">
          <Button asChild>
            <Link href="/campaigns/simulation">Open Detailed Simulation Engine</Link>
          </Button>
          <Button variant="secondary" onClick={onRunPreview} disabled={loading}>
            {loading ? "Running..." : "Run Portfolio Simulation"}
          </Button>
        </CardContent>
      </Card>

      {error ? <p className="text-sm text-red-600">{error}</p> : null}

      <section className="grid gap-3 md:grid-cols-3">
        {forecasts.map((item) => (
          <Card key={item.metric}>
            <CardHeader>
              <CardDescription>{item.metric}</CardDescription>
              <CardTitle className="text-2xl">{item.value}</CardTitle>
            </CardHeader>
          </Card>
        ))}
      </section>
    </div>
  );
}
