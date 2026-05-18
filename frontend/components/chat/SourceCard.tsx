import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import type { ChatSource } from '@/lib/types';
import { Badge } from '@/components/ui/badge';
import { truncate } from '@/lib/utils';

export function SourceCard({ source }: { source: ChatSource }) {
  return (
    <Card className="border border-indigo-400/20 bg-indigo-500/10">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between gap-2">
          <CardTitle className="text-sm">{source.project_name}</CardTitle>
          <Badge tone="muted">{source.chunk_type}</Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-2">
        <div className="text-sm text-slate-200">{truncate(source.content, 180)}</div>
        <div className="text-xs text-slate-400">Score: {source.score.toFixed(2)}</div>
      </CardContent>
    </Card>
  );
}
