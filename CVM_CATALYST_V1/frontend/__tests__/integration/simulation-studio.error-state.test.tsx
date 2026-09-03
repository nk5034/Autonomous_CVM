import { fireEvent, render, screen, waitFor } from "@testing-library/react";

import SimulationStudioPage from "@/app/(enterprise)/simulation-studio/page";

jest.mock("@/lib/api/enterprise", () => ({
  runEnterpriseSimulationPreview: jest.fn().mockResolvedValue(null),
}));

describe("Simulation Studio error state", () => {
  it("shows an error message when live preview fails", async () => {
    render(<SimulationStudioPage />);

    fireEvent.click(screen.getByRole("button", { name: "Run Portfolio Simulation" }));

    await waitFor(() => {
      expect(screen.getByText("Simulation preview failed. Verify backend availability.")).toBeInTheDocument();
    });
  });
});
