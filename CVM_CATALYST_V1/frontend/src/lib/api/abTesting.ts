import type { ABTestingRequest, ABTestingResponse, ABTestingTemplateResponse } from "@/types/abTesting";

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

export async function getABTestingTemplate(): Promise<ABTestingTemplateResponse> {
  return callApi<ABTestingTemplateResponse>("/ab-testing/template");
}

export async function runABTesting(payload: ABTestingRequest): Promise<ABTestingResponse> {
  return callApi<ABTestingResponse>("/ab-testing/run", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}