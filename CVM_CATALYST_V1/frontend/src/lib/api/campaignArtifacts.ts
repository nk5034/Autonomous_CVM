import type { ArtifactExportResponse, ArtifactType, CampaignArtifact } from "@/types/campaignArtifacts";

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

export async function generateArtifact(
  campaignId: number,
  artifactType: ArtifactType,
  content: Record<string, unknown>,
  author: string,
): Promise<CampaignArtifact> {
  return callApi<CampaignArtifact>(`/campaign-artifacts/${campaignId}/generate`, {
    method: "POST",
    body: JSON.stringify({ artifact_type: artifactType, content, author }),
  });
}

export async function listVersions(campaignId: number, artifactType: ArtifactType): Promise<CampaignArtifact[]> {
  return callApi<CampaignArtifact[]>(`/campaign-artifacts/${campaignId}/${artifactType}/versions`);
}

export async function submitForApproval(campaignId: number, artifactType: ArtifactType): Promise<CampaignArtifact> {
  return callApi<CampaignArtifact>(`/campaign-artifacts/${campaignId}/${artifactType}/approval/submit`, {
    method: "POST",
    body: "{}",
  });
}

export async function reviewArtifact(
  campaignId: number,
  artifactType: ArtifactType,
  reviewer: string,
  approve: boolean,
  comment?: string,
): Promise<CampaignArtifact> {
  return callApi<CampaignArtifact>(`/campaign-artifacts/${campaignId}/${artifactType}/approval/review`, {
    method: "POST",
    body: JSON.stringify({ reviewer, approve, comment }),
  });
}

export async function rollbackArtifact(
  campaignId: number,
  artifactType: ArtifactType,
  targetVersion: number,
  actor: string,
): Promise<CampaignArtifact> {
  return callApi<CampaignArtifact>(`/campaign-artifacts/${campaignId}/${artifactType}/rollback`, {
    method: "POST",
    body: JSON.stringify({ target_version: targetVersion, actor }),
  });
}

export async function exportExcel(campaignId: number): Promise<ArtifactExportResponse> {
  return callApi<ArtifactExportResponse>(`/campaign-artifacts/${campaignId}/exports/excel`, {
    method: "POST",
    body: "{}",
  });
}

export async function exportWord(campaignId: number): Promise<ArtifactExportResponse> {
  return callApi<ArtifactExportResponse>(`/campaign-artifacts/${campaignId}/exports/word`, {
    method: "POST",
    body: "{}",
  });
}
