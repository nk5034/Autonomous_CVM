import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";

export default function CampaignConfigurationPage() {
  return (
    <div className="grid gap-4 lg:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle>Campaign Configuration</CardTitle>
          <CardDescription>Define channels, cadence, caps, and proposition mapping.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <Input defaultValue="Retention Pulse Q4" />
          <Select defaultValue="omni-channel">
            <option value="omni-channel">Omni-channel</option>
            <option value="email-first">Email-first</option>
            <option value="sms-first">SMS-first</option>
          </Select>
          <Input type="number" defaultValue="120000" />
          <Textarea rows={6} defaultValue="Contact policy: max 2 touches in 14 days. Exclude VIP opt-out list." />
          <Button>Validate Configuration</Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Constraint Monitor</CardTitle>
          <CardDescription>Live checks from simulation and treatment metadata agents.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-2 text-sm">
          <p>Channel saturation: within limit</p>
          <p>Audience volume floor: passed</p>
          <p>Control-group split consistency: warning (9.2% target vs 10% policy)</p>
          <p>Expected spend band: $412k - $448k</p>
        </CardContent>
      </Card>
    </div>
  );
}
