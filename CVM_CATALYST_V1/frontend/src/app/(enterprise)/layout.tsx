import { EnterpriseShell } from "@/components/layouts/enterprise-shell";

export default function EnterpriseLayout({ children }: { children: React.ReactNode }) {
  return <EnterpriseShell>{children}</EnterpriseShell>;
}
