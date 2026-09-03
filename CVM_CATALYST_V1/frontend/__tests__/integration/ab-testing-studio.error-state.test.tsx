import { fireEvent, render, screen, waitFor } from "@testing-library/react";

import ABTestingStudioPage from "@/app/(enterprise)/ab-testing-studio/page";

jest.mock("@/lib/api/enterprise", () => ({
  runEnterpriseABPreview: jest.fn().mockResolvedValue(null),
}));

describe("AB Testing Studio error state", () => {
  it("shows an error message when live AB preview fails", async () => {
    render(<ABTestingStudioPage />);

    fireEvent.click(screen.getByRole("button", { name: "Run Live AB Preview" }));

    await waitFor(() => {
      expect(screen.getByText("A/B preview failed. Verify backend availability.")).toBeInTheDocument();
    });
  });
});
