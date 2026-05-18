import { Badge } from '@/components/ui/badge';

export function TechStackBadge({ label }: { label: string }) {
  return <Badge tone="muted" className="border-white/10 bg-white/5 text-slate-200">{label}</Badge>;
}
