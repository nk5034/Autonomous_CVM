export type ArtifactType =
  | "selection_briefing"
  | "audience_definition"
  | "campaign_configuration"
  | "proposition_sheet"
  | "treatment_sheet"
  | "contact_rules"
  | "volume_constraints"
  | "control_group_definition"
  | "reporting_configuration";

export interface CampaignArtifact {
  id: string;
  campaign_id: number;
  artifact_type: ArtifactType;
  title: string;
  version: number;
  status: "draft" | "pending_approval" | "approved" | "rejected" | "rolled_back";
  content: Record<string, unknown>;
  author: string;
  approver?: string | null;
  approval_comment?: string | null;
  created_at?: string;
  updated_at?: string;
}

export interface ArtifactExportResponse {
  format: string;
  path: string;
}
