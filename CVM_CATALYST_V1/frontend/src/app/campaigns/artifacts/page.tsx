"use client";

import { FormEvent, useMemo, useState } from "react";

import {
  exportExcel,
  exportWord,
  generateArtifact,
  listVersions,
  reviewArtifact,
  rollbackArtifact,
  submitForApproval,
} from "@/lib/api/campaignArtifacts";
import type { ArtifactType, CampaignArtifact } from "@/types/campaignArtifacts";

const artifactTypes: ArtifactType[] = [
  "selection_briefing",
  "audience_definition",
  "campaign_configuration",
  "proposition_sheet",
  "treatment_sheet",
  "contact_rules",
  "volume_constraints",
  "control_group_definition",
  "reporting_configuration",
];

export default function CampaignArtifactsPage() {
  const [campaignId, setCampaignId] = useState<number>(500);
  const [artifactType, setArtifactType] = useState<ArtifactType>("selection_briefing");
  const [author, setAuthor] = useState("planner.user");
  const [reviewer, setReviewer] = useState("manager.user");
  const [rollbackVersion, setRollbackVersion] = useState<number>(1);
  const [contentText, setContentText] = useState('{"objective":"increase retention"}');
  const [result, setResult] = useState<unknown>(null);
  const [history, setHistory] = useState<CampaignArtifact[]>([]);
  const [error, setError] = useState<string>("");

  const prettyHistory = useMemo(() => JSON.stringify(history, null, 2), [history]);

  const parseContent = (): Record<string, unknown> => {
    try {
      return JSON.parse(contentText) as Record<string, unknown>;
    } catch {
      throw new Error("Content must be valid JSON.");
    }
  };

  const run = async (operation: () => Promise<unknown>) => {
    setError("");
    try {
      const response = await operation();
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Request failed");
    }
  };

  const onGenerate = async (event: FormEvent) => {
    event.preventDefault();
    await run(() => generateArtifact(campaignId, artifactType, parseContent(), author));
  };

  return (
    <main className="artifact-page">
      <h1>Campaign Artifacts Workspace</h1>
      <p>DB-backed flow: generation, approval workflow, rollback, and Word/Excel exports.</p>

      <div className="grid two">
        <section className="card">
          <h2>Generate Artifact</h2>
          <form onSubmit={onGenerate}>
            <label>Campaign ID</label>
            <input
              type="number"
              value={campaignId}
              onChange={(event) => setCampaignId(Number(event.target.value))}
            />

            <label>Artifact Type</label>
            <select
              value={artifactType}
              onChange={(event) => setArtifactType(event.target.value as ArtifactType)}
            >
              {artifactTypes.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>

            <label>Author</label>
            <input value={author} onChange={(event) => setAuthor(event.target.value)} />

            <label>Content JSON</label>
            <textarea
              rows={6}
              value={contentText}
              onChange={(event) => setContentText(event.target.value)}
            />

            <button type="submit">Generate</button>
          </form>
        </section>

        <section className="card">
          <h2>Approval And Rollback</h2>
          <label>Reviewer</label>
          <input value={reviewer} onChange={(event) => setReviewer(event.target.value)} />

          <div className="row">
            <button onClick={() => run(() => submitForApproval(campaignId, artifactType))}>
              Submit For Approval
            </button>
            <button className="secondary" onClick={() => run(() => reviewArtifact(campaignId, artifactType, reviewer, true, "approved"))}>
              Approve
            </button>
            <button className="secondary" onClick={() => run(() => reviewArtifact(campaignId, artifactType, reviewer, false, "rejected"))}>
              Reject
            </button>
          </div>

          <label>Rollback Target Version</label>
          <input
            type="number"
            value={rollbackVersion}
            onChange={(event) => setRollbackVersion(Number(event.target.value))}
          />
          <button onClick={() => run(() => rollbackArtifact(campaignId, artifactType, rollbackVersion, author))}>
            Rollback
          </button>

          <h3 style={{ marginTop: 18 }}>Exports</h3>
          <div className="row">
            <button onClick={() => run(() => exportExcel(campaignId))}>Export Excel</button>
            <button onClick={() => run(() => exportWord(campaignId))}>Export Word</button>
          </div>
        </section>
      </div>

      <section className="card" style={{ marginTop: 16 }}>
        <h2>Version History</h2>
        <button
          onClick={async () => {
            setError("");
            try {
              const versions = await listVersions(campaignId, artifactType);
              setHistory(versions);
              setResult(versions.at(-1) || null);
            } catch (err) {
              setError(err instanceof Error ? err.message : "Request failed");
            }
          }}
        >
          Refresh Versions
        </button>
        <pre className="pre">{prettyHistory || "[]"}</pre>
      </section>

      <section className="card" style={{ marginTop: 16 }}>
        <h2>Last API Result</h2>
        {error ? <p style={{ color: "#b42318" }}>{error}</p> : null}
        <pre className="pre">{result ? JSON.stringify(result, null, 2) : "No response yet."}</pre>
      </section>
    </main>
  );
}
