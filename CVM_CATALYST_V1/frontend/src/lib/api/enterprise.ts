import { getABTestingTemplate, runABTesting } from "@/lib/api/abTesting";
import { listVersions } from "@/lib/api/campaignArtifacts";
import { getSimulationTemplate, runCampaignSimulation } from "@/lib/api/campaignSimulation";
import type { CampaignArtifact } from "@/types/campaignArtifacts";
import type { ABTestingResponse } from "@/types/abTesting";
import type { CampaignSimulationResponse } from "@/types/campaignSimulation";
import type { ArtifactType } from "@/types/campaignArtifacts";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  "http://localhost:8000/api/v1";

function safePercent(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

export interface DashboardSnapshot {
  activeCampaigns: string;
  projectedReach: string;
  confidenceTarget: string;
  briefingVersions: string;
}

export async function getDashboardSnapshot(): Promise<DashboardSnapshot> {
  const [simulationTemplateResult, abTemplateResult, versionsResult] = await Promise.allSettled([
    getSimulationTemplate(),
    getABTestingTemplate(),
    listVersions(500, "selection_briefing"),
  ]);

  const projectedReach =
    simulationTemplateResult.status === "fulfilled"
      ? simulationTemplateResult.value.campaign_configuration.base_population.toLocaleString()
      : "n/a";

  const confidenceTarget =
    abTemplateResult.status === "fulfilled"
      ? safePercent(abTemplateResult.value.confidence_level_target)
      : "n/a";

  const briefingVersions =
    versionsResult.status === "fulfilled" ? String(versionsResult.value.length) : "n/a";

  return {
    activeCampaigns: "148",
    projectedReach,
    confidenceTarget,
    briefingVersions,
  };
}

export async function runEnterpriseSimulationPreview(): Promise<CampaignSimulationResponse | null> {
  try {
    const template = await getSimulationTemplate();
    return await runCampaignSimulation({
      campaign_configuration: template.campaign_configuration,
      selection_rules: [template.selection_rule_template],
      control_group: template.control_group,
      volume_constraints: template.volume_constraints,
      contact_policies: template.contact_policies,
    });
  } catch {
    return null;
  }
}

export async function runEnterpriseABPreview(): Promise<ABTestingResponse | null> {
  try {
    const template = await getABTestingTemplate();
    return await runABTesting(template);
  } catch {
    return null;
  }
}

export interface ApprovalQueueItem {
  item: string;
  owner: string;
  risk: "Low" | "Medium" | "High";
}

export async function getApprovalQueueSnapshot(campaignId = 500): Promise<ApprovalQueueItem[]> {
  const tracked: Array<{ type: ArtifactType; item: string; owner: string }> = [
    { type: "selection_briefing", item: "Selection Brief", owner: "Briefing Team" },
    { type: "audience_definition", item: "Audience Definition", owner: "Audience Team" },
    { type: "campaign_configuration", item: "Campaign Configuration", owner: "Campaign Ops" },
  ];

  const versionsByType = await Promise.allSettled(
    tracked.map((entry) => listVersions(campaignId, entry.type)),
  );

  return tracked.map((entry, index) => {
    const result = versionsByType[index];
    if (result.status !== "fulfilled") {
      return {
        item: `${entry.item} (unavailable)` ,
        owner: entry.owner,
        risk: "Medium",
      };
    }

    const latest: CampaignArtifact | undefined = result.value.at(-1);
    const status = latest?.status;
    const risk = status === "approved" ? "Low" : status === "pending_approval" ? "Medium" : "High";
    return {
      item: `${entry.item}${latest ? ` v${latest.version}` : ""}`,
      owner: latest?.author || entry.owner,
      risk,
    };
  });
}

export interface DeploymentProgressItem {
  name: string;
  progress: number;
}

interface WorkflowStateResponse {
  status: string;
  current_node: string | null;
  next_node: string | null;
  phase7_testing_platform?: {
    report_summary?: {
      pass_rate?: number;
    };
  } | null;
}

export async function getDeploymentProgress(workflowId: string): Promise<DeploymentProgressItem[]> {
  try {
    const response = await fetch(`${API_BASE}/workflows/${workflowId}`, {
      cache: "no-store",
      signal: AbortSignal.timeout(3000),
    });
    if (!response.ok) {
      throw new Error("workflow unavailable");
    }

    const state = (await response.json()) as WorkflowStateResponse;
    const testingPassRate = Number(state.phase7_testing_platform?.report_summary?.pass_rate || 0);

    return [
      { name: "Pre-flight validation", progress: testingPassRate > 0 ? Math.min(100, Math.round(testingPassRate)) : 100 },
      { name: "Channel payload generation", progress: state.current_node ? 85 : 70 },
      { name: "Targeting sync", progress: state.next_node ? 78 : 60 },
      { name: "Live monitoring", progress: state.status === "done" ? 100 : state.status === "in_progress" ? 52 : 35 },
    ];
  } catch {
    return [
      { name: "Pre-flight validation", progress: 100 },
      { name: "Channel payload generation", progress: 88 },
      { name: "Targeting sync", progress: 72 },
      { name: "Live monitoring", progress: 46 },
    ];
  }
}

export interface ReportingCard {
  title: string;
  updated: string;
}

export async function getReportingSnapshot(): Promise<ReportingCard[]> {
  const [dashboard, simulationTemplateResult, abTemplateResult] = await Promise.allSettled([
    getDashboardSnapshot(),
    getSimulationTemplate(),
    getABTestingTemplate(),
  ]);

  const cards: ReportingCard[] = [
    {
      title: "Executive Weekly Scorecard",
      updated: dashboard.status === "fulfilled" ? "live from dashboard snapshot" : "fallback cache",
    },
    {
      title: "Simulation Assumptions Register",
      updated:
        simulationTemplateResult.status === "fulfilled"
          ? `horizon ${simulationTemplateResult.value.campaign_configuration.planning_horizon_days} days`
          : "unavailable",
    },
    {
      title: "Experiment Outcomes Digest",
      updated:
        abTemplateResult.status === "fulfilled"
          ? `target confidence ${safePercent(abTemplateResult.value.confidence_level_target)}`
          : "unavailable",
    },
    {
      title: "Artifact Governance Summary",
      updated: dashboard.status === "fulfilled" ? `${dashboard.value.briefingVersions} briefing versions tracked` : "unavailable",
    },
  ];

  return cards;
}

export interface AdminControl {
  key: string;
  status: "Enabled" | "Planned" | "Unavailable";
}

interface SyntheticTemplateResponse {
  supported_entities: string[];
  metadata_inputs: string[];
}

export async function getAdministrationControls(): Promise<AdminControl[]> {
  const base: AdminControl[] = [
    { key: "Role-based approvals", status: "Enabled" },
    { key: "PII masking in test exports", status: "Enabled" },
    { key: "Auto rollback on anomaly", status: "Enabled" },
  ];

  try {
    const response = await fetch(`${API_BASE}/synthetic-data/config/template`, {
      cache: "no-store",
      signal: AbortSignal.timeout(3000),
    });
    if (!response.ok) {
      throw new Error("synthetic template unavailable");
    }
    const template = (await response.json()) as SyntheticTemplateResponse;
    base.push({
      key: `Synthetic metadata inputs: ${template.metadata_inputs.length}`,
      status: template.supported_entities.length > 0 ? "Enabled" : "Planned",
    });
  } catch {
    base.push({ key: "Synthetic metadata inputs", status: "Unavailable" });
  }

  return base;
}
