import type { LucideIcon } from "lucide-react";
import {
  Activity,
  BarChart3,
  BriefcaseBusiness,
  Cog,
  FlaskConical,
  Gauge,
  LayoutDashboard,
  Megaphone,
  Rocket,
  Settings2,
  ShieldCheck,
  Target,
  Users,
} from "lucide-react";

export interface NavItem {
  title: string;
  href: string;
  icon: LucideIcon;
  description: string;
}

export const enterpriseNav: NavItem[] = [
  { title: "Dashboard", href: "/dashboard", icon: LayoutDashboard, description: "Portfolio signal board" },
  { title: "Campaign Workspace", href: "/campaign-workspace", icon: BriefcaseBusiness, description: "Plan and orchestrate campaigns" },
  { title: "Selection Briefings", href: "/selection-briefings", icon: Megaphone, description: "Capture strategic intent" },
  { title: "Audience Designer", href: "/audience-designer", icon: Users, description: "Define and validate segments" },
  { title: "Campaign Configuration", href: "/campaign-configuration", icon: Settings2, description: "Rules, channels, constraints" },
  { title: "Test Studio", href: "/test-studio", icon: FlaskConical, description: "Construct and run scenarios" },
  { title: "Simulation Studio", href: "/simulation-studio", icon: Gauge, description: "Forecast impact and cost" },
  { title: "AB Testing Studio", href: "/ab-testing-studio", icon: Activity, description: "Evaluate uplift and confidence" },
  { title: "Approval Center", href: "/approval-center", icon: ShieldCheck, description: "Review and governance" },
  { title: "Deployment Center", href: "/deployment-center", icon: Rocket, description: "Release and monitor" },
  { title: "Reporting Center", href: "/reporting-center", icon: BarChart3, description: "Executive and operational reports" },
  { title: "Administration", href: "/administration", icon: Cog, description: "Tenants, policies, and controls" },
];

export const heroMetrics = [
  { label: "Active Campaigns", value: "148", delta: "+12.4%" },
  { label: "Projected Incremental Revenue", value: "$4.8M", delta: "+9.1%" },
  { label: "Experiments Running", value: "27", delta: "+5" },
  { label: "Pending Approvals", value: "19", delta: "-3" },
];

export const attentionFeed = [
  "Postpaid retention campaign has reached 93% deployment readiness.",
  "Two audience briefs are blocked by compliance metadata gaps.",
  "A/B experiment CVM-392 detected statistically significant uplift (p < 0.05).",
  "Simulation variance alert on roaming proposition cost assumptions.",
];
