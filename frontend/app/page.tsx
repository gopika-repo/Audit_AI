import Link from 'next/link';
import { Bot, Layers3, Sparkles, Database, ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';

const featureCards = [
  { title: 'AI Chat', description: 'Ask engineering questions with cited answers from the company knowledge base.', icon: Bot },
  { title: 'Project Explorer', description: 'Browse team projects, tech stacks, and AI domains in one place.', icon: Layers3 },
  { title: 'Knowledge Base', description: 'Search the RAG index for architecture decisions, workflows, and examples.', icon: Database }
];

const stats = [
  { label: 'Projects', value: '12' },
  { label: 'Knowledge Chunks', value: '48' },
  { label: 'AI-Powered', value: 'Yes' }
];

export default function HomePage() {
  return (
    <main className="mx-auto min-h-[calc(100vh-80px)] max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
      <section className="relative overflow-hidden rounded-[2rem] border border-white/10 bg-gradient-to-br from-indigo-700/70 via-violet-700/50 to-slate-950 px-6 py-16 shadow-glow sm:px-10 lg:px-16">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.18),transparent_28%)]" />
        <div className="relative max-w-3xl">
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/10 px-4 py-2 text-sm text-slate-100">
            <Sparkles className="h-4 w-4" />
            AI-Powered Engineering Onboarding
          </div>
          <h1 className="text-4xl font-semibold tracking-tight text-white sm:text-6xl">
            Your company&apos;s engineering brain.
          </h1>
          <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-200">
            Explore projects, search the knowledge base, and chat with an AI agent that understands your engineering stack, architecture, and practices.
          </p>
          <div className="mt-8 flex flex-wrap gap-4">
            <Button asChild size="lg">
              <Link href="/projects">
                Explore Projects
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
            <Button asChild size="lg" variant="secondary">
              <Link href="/chat">Ask AI</Link>
            </Button>
          </div>
        </div>
      </section>

      <section className="mt-10 grid gap-6 md:grid-cols-3">
        {featureCards.map((feature) => (
          <Card key={feature.title} className="border-white/10 bg-white/5">
            <CardContent className="p-6">
              <feature.icon className="h-6 w-6 text-indigo-300" />
              <h2 className="mt-4 text-xl font-semibold text-white">{feature.title}</h2>
              <p className="mt-3 text-sm leading-6 text-slate-300">{feature.description}</p>
            </CardContent>
          </Card>
        ))}
      </section>

      <section className="mt-10 grid gap-4 sm:grid-cols-3">
        {stats.map((stat) => (
          <Card key={stat.label} className="border-white/10 bg-white/5">
            <CardContent className="p-6 text-center">
              <div className="text-3xl font-semibold text-white">{stat.value}</div>
              <div className="mt-1 text-sm uppercase tracking-[0.2em] text-slate-400">{stat.label}</div>
            </CardContent>
          </Card>
        ))}
      </section>
    </main>
  );
}
