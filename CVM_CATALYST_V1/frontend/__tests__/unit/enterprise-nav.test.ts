import { enterpriseNav } from "@/lib/enterprise-nav";

describe("enterprise navigation", () => {
  it("contains all Phase 11 pages", () => {
    expect(enterpriseNav).toHaveLength(12);
  });

  it("has unique href entries", () => {
    const hrefs = enterpriseNav.map((item) => item.href);
    expect(new Set(hrefs).size).toBe(hrefs.length);
  });
});
