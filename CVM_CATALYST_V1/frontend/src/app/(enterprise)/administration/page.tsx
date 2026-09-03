import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { getAdministrationControls } from "@/lib/api/enterprise";

export default async function AdministrationPage() {
  const controls = await getAdministrationControls();

  return (
    <Card>
      <CardHeader>
        <CardTitle>Administration</CardTitle>
        <CardDescription>Manage platform governance, tenant controls, and operating policies.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        {controls.map((control) => (
          <div key={control.key} className="flex items-center justify-between rounded-xl border border-border p-3">
            <span className="text-sm">{control.key}</span>
            <Badge variant={control.status === "Enabled" ? "success" : "neutral"}>{control.status}</Badge>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
