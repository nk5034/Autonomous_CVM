import { render, screen } from "@testing-library/react";

import { EnterpriseShell } from "@/components/layouts/enterprise-shell";

jest.mock("next/navigation", () => ({
  usePathname: () => "/dashboard",
}));

describe("EnterpriseShell", () => {
  it("renders shell heading and child content", () => {
    render(
      <EnterpriseShell>
        <div>Child content test</div>
      </EnterpriseShell>,
    );

    expect(screen.getByText("Enterprise Frontend Workspace")).toBeInTheDocument();
    expect(screen.getByText("Child content test")).toBeInTheDocument();
    expect(screen.getAllByText("Dashboard").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Administration").length).toBeGreaterThan(0);
  });
});
