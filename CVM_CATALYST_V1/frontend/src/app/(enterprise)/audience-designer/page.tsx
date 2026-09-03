import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";

const segments = [
  { name: "High Churn Risk + Premium ARPU", match: 61, policy: "Pass" },
  { name: "Silent Roamers", match: 43, policy: "Review" },
  { name: "Price Sensitive Youth", match: 38, policy: "Pass" },
];

export default function AudienceDesignerPage() {
  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Audience Designer</CardTitle>
          <CardDescription>Compose rules and monitor segment feasibility with governance overlays.</CardDescription>
        </CardHeader>
      </Card>

      <section className="grid gap-3 lg:grid-cols-3">
        {segments.map((segment) => (
          <Card key={segment.name}>
            <CardHeader>
              <CardTitle className="text-base">{segment.name}</CardTitle>
              <CardDescription>Estimated match rate</CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              <Progress value={segment.match} />
              <div className="flex items-center justify-between">
                <span className="text-sm">{segment.match}%</span>
                <Badge variant={segment.policy === "Pass" ? "success" : "warning"}>{segment.policy}</Badge>
              </div>
            </CardContent>
          </Card>
        ))}
      </section>
    </div>
  );
}
