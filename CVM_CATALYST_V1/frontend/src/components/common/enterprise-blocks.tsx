import { ArrowUpRight } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";

export function KpiGrid({
  items,
}: {
  items: Array<{ label: string; value: string; delta: string }>;
}) {
  return (
    <section className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
      {items.map((item, index) => (
        <Card key={item.label} className="animate-fade-up" style={{ animationDelay: `${index * 100}ms` }}>
          <CardHeader className="pb-3">
            <CardDescription>{item.label}</CardDescription>
            <CardTitle className="text-3xl">{item.value}</CardTitle>
          </CardHeader>
          <CardContent className="flex items-center justify-between pt-0">
            <Badge variant="success">{item.delta}</Badge>
            <ArrowUpRight className="h-4 w-4 text-muted-foreground" />
          </CardContent>
        </Card>
      ))}
    </section>
  );
}

export function StreamPanel({
  title,
  items,
}: {
  title: string;
  items: string[];
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        <CardDescription>High-priority signal stream from orchestration and governance agents.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        {items.map((item) => (
          <article key={item} className="rounded-xl border border-border bg-muted/40 p-3 text-sm leading-relaxed">
            {item}
          </article>
        ))}
      </CardContent>
    </Card>
  );
}

export function StageProgress({
  title,
  subtitle,
  progress,
}: {
  title: string;
  subtitle: string;
  progress: number;
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        <CardDescription>{subtitle}</CardDescription>
      </CardHeader>
      <CardContent>
        <Progress value={progress} />
        <p className="mt-2 text-xs text-muted-foreground">Completion: {progress}%</p>
      </CardContent>
    </Card>
  );
}
