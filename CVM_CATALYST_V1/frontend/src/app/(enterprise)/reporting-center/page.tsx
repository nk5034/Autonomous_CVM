import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { getReportingSnapshot } from "@/lib/api/enterprise";

export default async function ReportingCenterPage() {
  const reports = await getReportingSnapshot();

  return (
    <Card>
      <CardHeader>
        <CardTitle>Reporting Center</CardTitle>
        <CardDescription>Curate and schedule enterprise reporting packs for leadership and operations.</CardDescription>
      </CardHeader>
      <CardContent className="grid gap-3 md:grid-cols-2">
        {reports.map((report) => (
          <article key={report.title} className="rounded-xl border border-border bg-muted/40 p-3">
            <h3 className="font-medium">{report.title}</h3>
            <p className="text-sm text-muted-foreground">Updated {report.updated}</p>
          </article>
        ))}
      </CardContent>
    </Card>
  );
}
