import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

const activities = [
  '12 projects indexed into the knowledge base',
  '48 semantic chunks available for RAG',
  'AI chat agent ready for engineering questions'
];

export function RecentActivity() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Activity</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {activities.map((item) => (
          <div key={item} className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-slate-200">
            {item}
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
