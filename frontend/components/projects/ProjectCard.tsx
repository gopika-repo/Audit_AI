import Link from 'next/link';
import { ArrowRight, Bot } from 'lucide-react';
import { Card, CardContent, CardFooter, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { TechStackBadge } from './TechStackBadge';
import { truncate } from '@/lib/utils';
import type { Project } from '@/lib/types';

const domainToneMap: Record<string, 'default' | 'muted' | 'accent' | 'domain'> = {
  'Agentic AI': 'default',
  NLP: 'accent',
  'Computer Vision': 'muted',
  FinTech: 'domain',
  'Business Intelligence': 'domain',
  'Developer Tools': 'accent',
  'Conversational AI': 'default',
  'Document AI': 'default'
};

export function ProjectCard({ project }: { project: Project }) {
  const techStackPills = [
    ...project.tech_stack.languages,
    ...project.tech_stack.frameworks
  ].slice(0, 4);

  return (
    <Card className="group overflow-hidden transition duration-300 hover:-translate-y-1 hover:border-indigo-400/30 hover:bg-white/10">
      <CardHeader>
        <div className="flex items-start justify-between gap-4">
          <div>
            <CardTitle>{project.name}</CardTitle>
            <CardDescription className="mt-2 line-clamp-2">{truncate(project.description, 150)}</CardDescription>
          </div>
          <Badge tone={domainToneMap[project.domain] ?? 'muted'}>{project.domain}</Badge>
        </div>
        {project.ai_category ? <Badge tone="muted" className="w-fit">{project.ai_category}</Badge> : null}
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="flex flex-wrap gap-2">
          {techStackPills.map((item) => (
            <TechStackBadge key={item} label={item} />
          ))}
        </div>
      </CardContent>
      <CardFooter className="flex items-center justify-between gap-3">
        <Button asChild size="sm" variant="outline">
          <Link href={`/projects/${project.id}`}>
            View Details
            <ArrowRight className="ml-2 h-4 w-4" />
          </Link>
        </Button>
        <Button asChild size="sm">
          <Link href={`/chat?question=${encodeURIComponent(`Tell me about ${project.name}`)}`}>
            <Bot className="mr-2 h-4 w-4" />
            Ask AI
          </Link>
        </Button>
      </CardFooter>
    </Card>
  );
}
