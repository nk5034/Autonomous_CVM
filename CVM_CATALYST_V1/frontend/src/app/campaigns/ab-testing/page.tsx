"use client";

import { useMemo, useState } from "react";

import { getABTestingTemplate, runABTesting } from "@/lib/api/abTesting";
import type {
  ABDashboardSeriesPoint,
  ABTestingRequest,
  ABTestingResponse,
  ABVariantConfig,
} from "@/types/abTesting";

const defaultPayload: ABTestingRequest = {
  campaign_id: 700,
  experiment_name: "Welcome Offer Test",
  hypothesis: "Urgency-led messaging increases conversion.",
  audience_size: 100000,
  confidence_level_target: 0.95,
  control: {
    name: "control",
    traffic_percentage: 0.2,
    conversion_rate: 0.05,
  },
  variants: [
    {
      name: "variant_a",
      traffic_percentage: 0.4,
      conversion_rate: 0.057,
      description: "Personalized subject line",
    },
    {
      name: "variant_b",
      traffic_percentage: 0.4,
      conversion_rate: 0.061,
      description: "Urgency CTA",
    },
  ],
};

function num(value: number): string {
  return new Intl.NumberFormat("en-US").format(value);
}

function pct(value: number): string {
  return `${(value * 100).toFixed(2)}%`;
}

function BarList({
  title,
  points,
  percent,
}: {
  title: string;
  points: ABDashboardSeriesPoint[];
  percent?: boolean;
}) {
  const max = Math.max(1, ...points.map((point) => point.value));
  return (
    <section className="card sim-chart">
      <h3>{title}</h3>
      <div className="sim-bars">
        {points.map((point) => (
          <div key={point.label} className="sim-bar-row">
            <div className="sim-bar-header">
              <span>{point.label}</span>
              <strong>{percent ? pct(point.value) : num(Math.round(point.value))}</strong>
            </div>
            <div className="sim-track">
              <div className="sim-fill" style={{ width: `${(point.value / max) * 100}%` }} />
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

export default function ABTestingPage() {
  const [payload, setPayload] = useState<ABTestingRequest>(defaultPayload);
  const [result, setResult] = useState<ABTestingResponse | null>(null);
  const [error, setError] = useState<string>("");
  const [loading, setLoading] = useState(false);

  const kpis = useMemo(() => result?.dashboard.kpis || [], [result]);

  const updateVariant = (index: number, partial: Partial<ABVariantConfig>) => {
    const variants = [...payload.variants];
    variants[index] = { ...variants[index], ...partial };
    setPayload({ ...payload, variants });
  };

  const addVariant = () => {
    const count = payload.variants.length + 1;
    setPayload({
      ...payload,
      variants: [
        ...payload.variants,
        {
          name: `variant_${count}`,
          traffic_percentage: 0.1,
          conversion_rate: payload.control.conversion_rate,
          description: "New test treatment",
        },
      ],
    });
  };

  const removeVariant = (index: number) => {
    if (payload.variants.length <= 1) {
      return;
    }
    setPayload({
      ...payload,
      variants: payload.variants.filter((_, currentIndex) => currentIndex !== index),
    });
  };

  const run = async () => {
    setLoading(true);
    setError("");
    try {
      const response = await runABTesting(payload);
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "A/B test request failed");
    } finally {
      setLoading(false);
    }
  };

  const loadTemplate = async () => {
    setLoading(true);
    setError("");
    try {
      const template = await getABTestingTemplate();
      setPayload(template);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Template request failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="artifact-page sim-page ab-page">
      <h1>A/B Testing Framework</h1>
      <p>Create variants, allocate traffic, evaluate confidence and lift, and get rollout recommendations.</p>

      <section className="card sim-form">
        <h2>Experiment Configuration</h2>
        <div className="grid two">
          <div>
            <label>Campaign ID</label>
            <input
              type="number"
              value={payload.campaign_id}
              onChange={(event) => setPayload({ ...payload, campaign_id: Number(event.target.value) })}
            />

            <label>Experiment Name</label>
            <input
              value={payload.experiment_name}
              onChange={(event) => setPayload({ ...payload, experiment_name: event.target.value })}
            />

            <label>Hypothesis</label>
            <textarea
              rows={3}
              value={payload.hypothesis}
              onChange={(event) => setPayload({ ...payload, hypothesis: event.target.value })}
            />

            <label>Total Audience</label>
            <input
              type="number"
              value={payload.audience_size}
              onChange={(event) => setPayload({ ...payload, audience_size: Number(event.target.value) })}
            />
          </div>

          <div>
            <label>Confidence Target</label>
            <input
              type="number"
              step="0.01"
              value={payload.confidence_level_target}
              onChange={(event) =>
                setPayload({ ...payload, confidence_level_target: Number(event.target.value) })
              }
            />

            <label>Control Name</label>
            <input
              value={payload.control.name}
              onChange={(event) =>
                setPayload({
                  ...payload,
                  control: { ...payload.control, name: event.target.value },
                })
              }
            />

            <label>Control Traffic Allocation</label>
            <input
              type="number"
              step="0.01"
              value={payload.control.traffic_percentage}
              onChange={(event) =>
                setPayload({
                  ...payload,
                  control: { ...payload.control, traffic_percentage: Number(event.target.value) },
                })
              }
            />

            <label>Control Conversion Rate</label>
            <input
              type="number"
              step="0.001"
              value={payload.control.conversion_rate}
              onChange={(event) =>
                setPayload({
                  ...payload,
                  control: { ...payload.control, conversion_rate: Number(event.target.value) },
                })
              }
            />
          </div>
        </div>

        <h3>Variants</h3>
        <div className="grid">
          {payload.variants.map((variant, index) => (
            <div key={`${variant.name}-${index}`} className="card ab-variant-card">
              <div className="grid two">
                <div>
                  <label>Name</label>
                  <input
                    value={variant.name}
                    onChange={(event) => updateVariant(index, { name: event.target.value })}
                  />
                </div>
                <div>
                  <label>Traffic Allocation</label>
                  <input
                    type="number"
                    step="0.01"
                    value={variant.traffic_percentage}
                    onChange={(event) =>
                      updateVariant(index, { traffic_percentage: Number(event.target.value) })
                    }
                  />
                </div>
              </div>

              <div className="grid two">
                <div>
                  <label>Expected Conversion Rate</label>
                  <input
                    type="number"
                    step="0.001"
                    value={variant.conversion_rate}
                    onChange={(event) =>
                      updateVariant(index, { conversion_rate: Number(event.target.value) })
                    }
                  />
                </div>
                <div>
                  <label>Description</label>
                  <input
                    value={variant.description || ""}
                    onChange={(event) => updateVariant(index, { description: event.target.value })}
                  />
                </div>
              </div>

              <button className="secondary" onClick={() => removeVariant(index)}>
                Remove Variant
              </button>
            </div>
          ))}
        </div>

        <div className="row" style={{ marginTop: 10 }}>
          <button onClick={run} disabled={loading}>
            {loading ? "Running..." : "Run A/B Test Analysis"}
          </button>
          <button className="secondary" onClick={loadTemplate} disabled={loading}>
            Load API Template
          </button>
          <button className="secondary" onClick={addVariant}>
            Add Variant
          </button>
        </div>
      </section>

      {error ? <p style={{ color: "#b42318" }}>{error}</p> : null}

      {result ? (
        <>
          <section className="grid sim-kpis">
            {kpis.map((kpi) => (
              <article key={kpi.label} className="card sim-kpi-card">
                <p>{kpi.label}</p>
                <h2>{kpi.format === "percent" ? pct(kpi.value) : num(Math.round(kpi.value))}</h2>
              </article>
            ))}
          </section>

          <section className="grid two" style={{ marginTop: 16 }}>
            <BarList title="Traffic Allocation" points={result.dashboard.traffic_allocation} percent />
            <BarList title="Conversion Rate By Arm" points={result.dashboard.conversion_rates} percent />
          </section>

          <section className="grid two" style={{ marginTop: 16 }}>
            <BarList title="Relative Lift By Variant" points={result.dashboard.lift_by_variant} percent />
            <BarList title="Confidence By Variant" points={result.dashboard.confidence_by_variant} percent />
          </section>

          <section className="card" style={{ marginTop: 16 }}>
            <h3>Recommendation Engine Output</h3>
            <p>
              <strong>Action:</strong> {result.recommendation.action}
            </p>
            <p>
              <strong>Recommended Variant:</strong> {result.recommendation.recommended_variant || "None"}
            </p>
            <p>
              <strong>Rationale:</strong> {result.recommendation.rationale}
            </p>

            <h3 style={{ marginTop: 18 }}>Variant Performance</h3>
            <div className="pre">
              {JSON.stringify(result.variant_performance, null, 2)}
            </div>
          </section>
        </>
      ) : null}
    </main>
  );
}