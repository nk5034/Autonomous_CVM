"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

export default function TestStudioPage() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Test Studio</CardTitle>
        <CardDescription>Build functional, regression, and boundary test packs for campaign artifacts.</CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="functional">
          <TabsList>
            <TabsTrigger value="functional">Functional</TabsTrigger>
            <TabsTrigger value="negative">Negative</TabsTrigger>
            <TabsTrigger value="boundary">Boundary</TabsTrigger>
          </TabsList>
          <TabsContent value="functional" className="rounded-xl border border-border p-3 text-sm">
            34 scenarios generated. 32 passed in latest run.
          </TabsContent>
          <TabsContent value="negative" className="rounded-xl border border-border p-3 text-sm">
            11 scenarios generated. 2 policy exceptions flagged.
          </TabsContent>
          <TabsContent value="boundary" className="rounded-xl border border-border p-3 text-sm">
            Volume edge-case coverage at 87%. Add low-population cohort scenarios.
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}
