"use client";

import { useMemo } from 'react';
import Link from 'next/link';
import { ArrowRight, Bot, Search } from 'lucide-react';
import { useProjects } from '@/hooks/useProjects';
import { StatsCard } from '@/components/dashboard/StatsCard';
import { ProjectsGrid } from '@/components/dashboard/ProjectsGrid';
import { RecentActivity } from '@/components/dashboard/RecentActivity';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';

export default function DashboardPage() {
  const { data } = useProjects();
  const projects = data?.items ?? [];

  const domains = useMemo(() => Array.from(new Set(projects.map((project) => project.domain))), [projects]);
  const categories = useMemo(
    () => Array.from(new Set(projects.map((project) => project.ai_category).filter(Boolean) as string[])),
    [projects]
  );

  return (
    <main className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
      <section className="grid gap-4 md:grid-cols-4">
        <StatsCard label="Total Projects" value={String(data?.total ?? 12)} helper="Loaded from the backend" />
        <StatsCard label="AI Domains" value={String(domains.length || 6)} helper="Agentic AI, NLP, CV, and more" />
        <StatsCard label="Tech Stacks" value={String(categories.length || 8)} helper="Frameworks and tools used across teams" />
        <StatsCard label="Knowledge Chunks" value="48" helper="Indexed for semantic retrieval" />
      </section>

      <section className="mt-10 grid gap-6 lg:grid-cols-[minmax(0,1fr)_360px]">
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Project Preview</CardTitle>
            </CardHeader>
            <CardContent>
              <ProjectsGrid projects={projects.slice(0, 6)} />
            </CardContent>
          </Card>
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Quick AI Chat</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <Input placeholder="Ask about projects, RAG, or tech stacks..." aria-label="Quick AI chat input" />
              <Button asChild className="w-full">
                <Link href="/chat">
                  <Bot className="mr-2 h-4 w-4" />
                  Open AI Chat
                </Link>
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Domain Breakdown</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {domains.map((domain) => (
                <div key={domain} className="flex items-center justify-between rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-slate-200">
                  <span>{domain}</span>
                  <ArrowRight className="h-4 w-4 text-indigo-300" />
                </div>
              ))}
            </CardContent>
          </Card>

          <RecentActivity />
        </div>
      </section>
    </main>
  );
}
