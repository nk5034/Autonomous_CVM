"use client";

import { useMemo, useState } from "react";

import {
  getSimulationTemplate,
  runCampaignSimulation,
} from "@/lib/api/campaignSimulation";
import type {
  CampaignSimulationRequest,
  CampaignSimulationResponse,
  DashboardSeriesPoint,
} from "@/types/campaignSimulation";

const defaultPayload: CampaignSimulationRequest = {
  campaign_configuration: {
    campaign_name: "Q4 Retention Push",
    base_population: 120000,
    baseline_response_rate: 0.08,
    baseline_conversion_rate: 0.2,
    average_revenue_per_conversion: 140,
    planning_horizon_days: 30,
  },
  selection_rules: [
    {
      name: "High-risk churn segment",
      field: "churn_risk_band",
      operator: "in",
      value: ["high", "very_high"],
      estimated_match_rate: 0.62,
    },
    {
      name: "Digital reachable",
      field: "email_opt_in",
      operator: "eq",
      value: "true",
      estimated_match_rate: 0.81,
    },
  ],
  control_group: {
    enabled: true,
    holdout_ratio: 0.1,
  },
  volume_constraints: {
    min_audience: 10000,
    max_audience: 50000,
    max_contacts_total: 120000,
  },
  contact_policies: [
    {
      channel: "email",
      allocation_ratio: 0.7,
      max_contacts_per_customer: 2,
      unit_cost: 0.03,
      response_lift: 0.1,
      conversion_lift: 0.05,
    },
    {
      channel: "sms",
      allocation_ratio: 0.3,
      max_contacts_per_customer: 1,
      unit_cost: 0.08,
      response_lift: 0.25,
      conversion_lift: 0.08,
    },
  ],
};

function money(value: number): string {
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(value);
}

function num(value: number): string {
  return new Intl.NumberFormat("en-US").format(value);
}

function pct(value: number): string {
  return `${(value * 100).toFixed(2)}%`;
}

function BarList({ title, points }: { title: string; points: DashboardSeriesPoint[] }) {
  const max = Math.max(1, ...points.map((point) => point.value));
  return (
    <section className="card sim-chart">
      <h3>{title}</h3>
      <div className="sim-bars">
        {points.map((point) => (
          <div key={point.label} className="sim-bar-row">
            <div className="sim-bar-header">
              <span>{point.label}</span>
              <strong>{num(Math.round(point.value))}</strong>
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

export default function CampaignSimulationPage() {
  const [payload, setPayload] = useState<CampaignSimulationRequest>(defaultPayload);
  const [result, setResult] = useState<CampaignSimulationResponse | null>(null);
  const [error, setError] = useState<string>("");
  const [loading, setLoading] = useState(false);

  const kpis = useMemo(() => result?.dashboard.kpis || [], [result]);

  const runSimulation = async () => {
    setLoading(true);
    setError("");
    try {
      const response = await runCampaignSimulation(payload);
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Simulation request failed");
    } finally {
      setLoading(false);
    }
  };

  const loadTemplate = async () => {
    setLoading(true);
    setError("");
    try {
      const template = await getSimulationTemplate();
      setPayload({
        campaign_configuration: template.campaign_configuration,
        selection_rules: [template.selection_rule_template],
        control_group: template.control_group,
        volume_constraints: template.volume_constraints,
        contact_policies: template.contact_policies,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Template request failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="artifact-page sim-page">
      <h1>Campaign Simulation Engine</h1>
      <p>Forecast expected audience, response, costs, revenue, and ROI from planning assumptions.</p>

      <section className="card sim-form">
        <h2>Simulation Input</h2>
        <div className="grid two">
          <div>
            <label>Campaign Name</label>
            <input
              value={payload.campaign_configuration.campaign_name}
              onChange={(event) =>
                setPayload({
                  ...payload,
                  campaign_configuration: {
                    ...payload.campaign_configuration,
                    campaign_name: event.target.value,
                  },
                })
              }
            />

            <label>Base Population</label>
            <input
              type="number"
              value={payload.campaign_configuration.base_population}
              onChange={(event) =>
                setPayload({
                  ...payload,
                  campaign_configuration: {
                    ...payload.campaign_configuration,
                    base_population: Number(event.target.value),
                  },
                })
              }
            />

            <label>Baseline Response Rate</label>
            <input
              type="number"
              step="0.01"
              value={payload.campaign_configuration.baseline_response_rate}
              onChange={(event) =>
                setPayload({
                  ...payload,
                  campaign_configuration: {
                    ...payload.campaign_configuration,
                    baseline_response_rate: Number(event.target.value),
                  },
                })
              }
            />

            <label>Baseline Conversion Rate</label>
            <input
              type="number"
              step="0.01"
              value={payload.campaign_configuration.baseline_conversion_rate}
              onChange={(event) =>
                setPayload({
                  ...payload,
                  campaign_configuration: {
                    ...payload.campaign_configuration,
                    baseline_conversion_rate: Number(event.target.value),
                  },
                })
              }
            />
          </div>

          <div>
            <label>Average Revenue per Conversion</label>
            <input
              type="number"
              value={payload.campaign_configuration.average_revenue_per_conversion}
              onChange={(event) =>
                setPayload({
                  ...payload,
                  campaign_configuration: {
                    ...payload.campaign_configuration,
                    average_revenue_per_conversion: Number(event.target.value),
                  },
                })
              }
            />

            <label>Selection Rule 1 Match Rate</label>
            <input
              type="number"
              step="0.01"
              value={payload.selection_rules[0]?.estimated_match_rate || 0}
              onChange={(event) => {
                const rules = [...payload.selection_rules];
                if (!rules[0]) {
                  return;
                }
                rules[0] = { ...rules[0], estimated_match_rate: Number(event.target.value) };
                setPayload({ ...payload, selection_rules: rules });
              }}
            />

            <label>Control Holdout Ratio</label>
            <input
              type="number"
              step="0.01"
              value={payload.control_group.holdout_ratio}
              onChange={(event) =>
                setPayload({
                  ...payload,
                  control_group: {
                    ...payload.control_group,
                    holdout_ratio: Number(event.target.value),
                  },
                })
              }
            />

            <label>Max Audience</label>
            <input
              type="number"
              value={payload.volume_constraints.max_audience || 0}
              onChange={(event) =>
                setPayload({
                  ...payload,
                  volume_constraints: {
                    ...payload.volume_constraints,
                    max_audience: Number(event.target.value),
                  },
                })
              }
            />
          </div>
        </div>

        <div className="row">
          <button onClick={runSimulation} disabled={loading}>
            {loading ? "Running..." : "Run Simulation"}
          </button>
          <button className="secondary" onClick={loadTemplate} disabled={loading}>
            Load API Template
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
                <h2>
                  {kpi.format === "currency"
                    ? money(kpi.value)
                    : kpi.format === "percent"
                      ? pct(kpi.value)
                      : num(Math.round(kpi.value))}
                </h2>
              </article>
            ))}
          </section>

          <section className="grid two" style={{ marginTop: 16 }}>
            <BarList title="Audience Waterfall" points={result.dashboard.waterfall} />
            <BarList title="Channel Mix" points={result.dashboard.channel_mix} />
          </section>

          <section className="grid two" style={{ marginTop: 16 }}>
            <BarList title="Revenue vs Cost" points={result.dashboard.revenue_vs_cost} />
            <section className="card sim-chart">
              <h3>Forecast Details</h3>
              <p><strong>Expected Audience:</strong> {num(result.expected_audience.target_audience)}</p>
              <p><strong>Expected Responses:</strong> {num(result.response_forecast.expected_responses)}</p>
              <p><strong>Expected Conversions:</strong> {num(result.response_forecast.expected_conversions)}</p>
              <p><strong>Break-even Response Rate:</strong> {pct(result.roi_forecast.break_even_response_rate)}</p>
              <p><strong>Simulation ID:</strong> {result.simulation_id}</p>
            </section>
          </section>
        </>
      ) : null}
    </main>
  );
}
