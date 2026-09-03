export interface ABControlGroupConfig {
  name: string;
  traffic_percentage: number;
  conversion_rate: number;
}

export interface ABVariantConfig {
  name: string;
  traffic_percentage: number;
  conversion_rate: number;
  description?: string | null;
}

export interface ABTestingRequest {
  campaign_id: number;
  experiment_name: string;
  hypothesis: string;
  audience_size: number;
  confidence_level_target: number;
  control: ABControlGroupConfig;
  variants: ABVariantConfig[];
}

export interface ABExperimentArm {
  name: string;
  is_control: boolean;
  allocation: number;
  audience: number;
  conversion_rate: number;
  expected_conversions: number;
}

export interface ABVariantPerformance {
  name: string;
  lift: number;
  absolute_lift: number;
  z_score: number;
  p_value: number;
  confidence: number;
  statistically_significant: boolean;
  incremental_conversions: number;
}

export interface ABRecommendation {
  action: string;
  rationale: string;
  recommended_variant?: string | null;
}

export interface ABDashboardKPI {
  label: string;
  value: number;
  format: "number" | "currency" | "percent";
}

export interface ABDashboardSeriesPoint {
  label: string;
  value: number;
}

export interface ABTestingResponse {
  experiment_id: string;
  generated_at: string;
  campaign_id: number;
  experiment_name: string;
  hypothesis: string;
  confidence_level_target: number;
  arms: ABExperimentArm[];
  variant_performance: ABVariantPerformance[];
  recommendation: ABRecommendation;
  dashboard: {
    kpis: ABDashboardKPI[];
    traffic_allocation: ABDashboardSeriesPoint[];
    conversion_rates: ABDashboardSeriesPoint[];
    lift_by_variant: ABDashboardSeriesPoint[];
    confidence_by_variant: ABDashboardSeriesPoint[];
  };
}

export interface ABTestingTemplateResponse extends ABTestingRequest {}