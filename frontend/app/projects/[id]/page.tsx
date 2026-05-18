import Link from 'next/link';
import { notFound } from 'next/navigation';
import { Bot, ExternalLink, Layers3 } from 'lucide-react';
import { projectsApi } from '@/lib/api';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { TechStackBadge } from '@/components/projects/TechStackBadge';

export default async function ProjectDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;

  try {
    const project = await projectsApi.getById(id);

    return (
      <main className="mx-auto max-w-5xl px-4 py-10 sm:px-6 lg:px-8">
        <section className="rounded-[2rem] border border-white/10 bg-white/5 p-8 backdrop-blur-xl">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <Badge tone="default">{project.domain}</Badge>
              <h1 className="mt-4 text-4xl font-semibold text-white">{project.name}</h1>
              <p className="mt-4 max-w-3xl text-lg leading-8 text-slate-300">{project.description}</p>
            </div>
            <Button asChild variant="secondary">
              <Link href={`/chat?question=${encodeURIComponent(`Explain the ${project.name} project`)}`}>
                <Bot className="mr-2 h-4 w-4" />
                Ask AI about this project
              </Link>
            </Button>
          </div>
        </section>

        <section className="mt-8 grid gap-6 lg:grid-cols-[1fr_320px]">
          <Card>
            <CardHeader>
              <CardTitle>Tech Stack</CardTitle>
            </CardHeader>
            <CardContent className="space-y-5">
              <div>
                <div className="mb-3 text-sm font-medium text-slate-300">Languages</div>
                <div className="flex flex-wrap gap-2">
                  {project.tech_stack.languages.map((item) => (
                    <TechStackBadge key={item} label={item} />
                  ))}
                </div>
              </div>
              <div>
                <div className="mb-3 text-sm font-medium text-slate-300">Frameworks</div>
                <div className="flex flex-wrap gap-2">
                  {project.tech_stack.frameworks.map((item) => (
                    <TechStackBadge key={item} label={item} />
                  ))}
                </div>
              </div>
              <div>
                <div className="mb-3 text-sm font-medium text-slate-300">Tools</div>
                <div className="flex flex-wrap gap-2">
                  {project.tech_stack.tools.map((item) => (
                    <TechStackBadge key={item} label={item} />
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Project Info</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 text-sm text-slate-300">
              <div className="flex items-center justify-between gap-3 rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
                <span>AI Category</span>
                <Badge tone="muted">{project.ai_category ?? 'Uncategorized'}</Badge>
              </div>
              <div className="flex items-center justify-between gap-3 rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
                <span>Status</span>
                <Badge tone="muted">{project.is_active ? 'Active' : 'Inactive'}</Badge>
              </div>
              {project.repo_url ? (
                <Button asChild variant="outline" className="w-full">
                  <a href={project.repo_url} target="_blank" rel="noreferrer">
                    <ExternalLink className="mr-2 h-4 w-4" />
                    Repository
                  </a>
                </Button>
              ) : null}
            </CardContent>
          </Card>
        </section>
      </main>
    );
  } catch {
    notFound();
  }
}
