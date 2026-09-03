export type RuleOperator =
  | "eq"
  | "ne"
  | "gt"
  | "gte"
  | "lt"
  | "lte"
  | "in"
  | "not_in"
  | "between";

export interface CampaignConfiguration {
  campaign_name: string;
  base_population: number;
  baseline_response_rate: number;
  baseline_conversion_rate: number;
  average_revenue_per_conversion: number;
  planning_horizon_days: number;
}

export interface SelectionRule {
  name: string;
  field: string;
  operator: RuleOperator;
  value: string | number | Array<string | number>;
  estimated_match_rate: number;
}

export interface ControlGroupConfig {
  enabled: boolean;
  holdout_ratio: number;
}

export interface VolumeConstraints {
  min_audience: number;
  max_audience?: number | null;
  max_contacts_total?: number | null;
}

export interface ContactPolicy {
  channel: string;
  allocation_ratio: number;
  max_contacts_per_customer: number;
  unit_cost: number;
  response_lift: number;
  conversion_lift: number;
}

export interface CampaignSimulationRequest {
  campaign_configuration: CampaignConfiguration;
  selection_rules: SelectionRule[];
  control_group: ControlGroupConfig;
  volume_constraints: VolumeConstraints;
  contact_policies: ContactPolicy[];
}

export interface DashboardKPI {
  label: string;
  value: number;
  format: "number" | "currency" | "percent";
}

export interface DashboardSeriesPoint {
  label: string;
  value: number;
}

export interface CampaignSimulationResponse {
  simulation_id: string;
  generated_at: string;
  expected_audience: {
    base_population: number;
    eligible_audience: number;
    control_group_size: number;
    target_audience: number;
  };
  waterfall_analysis: {
    stages: Array<{ stage: string; count: number; retention_rate: number }>;
  };
  revenue_forecast: {
    expected_revenue: number;
    expected_conversions: number;
    average_revenue_per_conversion: number;
  };
  cost_forecast: {
    expected_cost: number;
    cost_per_contact: number;
    channel_breakdown: Array<{
      channel: string;
      audience: number;
      contacts: number;
      cost: number;
      response_rate: number;
      responses: number;
    }>;
  };
  response_forecast: {
    baseline_response_rate: number;
    effective_response_rate: number;
    expected_responses: number;
    expected_conversions: number;
  };
  roi_forecast: {
    roi: number;
    incremental_profit: number;
    break_even_response_rate: number;
  };
  dashboard: {
    kpis: DashboardKPI[];
    waterfall: DashboardSeriesPoint[];
    channel_mix: DashboardSeriesPoint[];
    revenue_vs_cost: DashboardSeriesPoint[];
  };
}

export interface CampaignSimulationTemplateResponse {
  campaign_configuration: CampaignConfiguration;
  selection_rule_template: SelectionRule;
  control_group: ControlGroupConfig;
  volume_constraints: VolumeConstraints;
  contact_policies: ContactPolicy[];
}
