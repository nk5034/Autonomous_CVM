import type {
  CampaignSimulationRequest,
  CampaignSimulationResponse,
  CampaignSimulationTemplateResponse,
} from "@/types/campaignSimulation";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  "http://localhost:8000/api/v1";

async function callApi<T>(path: string, init: RequestInit = {}): Promise<T> {
  const timeoutSignal = AbortSignal.timeout(3000);
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    signal: init.signal || timeoutSignal,
    headers: {
      "Content-Type": "application/json",
      ...(init.headers || {}),
    },
    cache: "no-store",
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || `Request failed with status ${response.status}`);
  }

  return (await response.json()) as T;
}

export async function getSimulationTemplate(): Promise<CampaignSimulationTemplateResponse> {
  return callApi<CampaignSimulationTemplateResponse>("/campaign-simulation/config/template");
}

export async function runCampaignSimulation(
  payload: CampaignSimulationRequest,
): Promise<CampaignSimulationResponse> {
  return callApi<CampaignSimulationResponse>("/campaign-simulation/run", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
