import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { getDeploymentProgress } from "@/lib/api/enterprise";

export default async function DeploymentCenterPage() {
  const phases = await getDeploymentProgress("wf_phase7_12001");

  return (
    <Card>
      <CardHeader>
        <CardTitle>Deployment Center</CardTitle>
        <CardDescription>Release management for approved campaigns with phased rollout controls.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {phases.map((phase) => (
          <div key={phase.name}>
            <div className="mb-1 flex items-center justify-between text-sm">
              <span>{phase.name}</span>
              <span>{phase.progress}%</span>
            </div>
            <Progress value={phase.progress} />
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
