import { Card, CardContent } from '@/components/ui/card';

export function StatsCard({ label, value, helper }: { label: string; value: string; helper: string }) {
  return (
    <Card className="bg-gradient-to-br from-white/10 to-white/5">
      <CardContent className="p-5">
        <div className="text-sm text-slate-300">{label}</div>
        <div className="mt-2 text-3xl font-semibold text-white">{value}</div>
        <div className="mt-2 text-sm text-slate-400">{helper}</div>
      </CardContent>
    </Card>
  );
}
