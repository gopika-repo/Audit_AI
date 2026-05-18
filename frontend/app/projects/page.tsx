"use client";

import { useMemo, useState } from 'react';
import { useProjects, useProjectSearch } from '@/hooks/useProjects';
import { ProjectFilter } from '@/components/projects/ProjectFilter';
import { ProjectCard } from '@/components/projects/ProjectCard';

export default function ProjectsPage() {
  const [query, setQuery] = useState<string>('');
  const [selectedDomain, setSelectedDomain] = useState<string>('all');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  const { data } = useProjects();
  const searchResult = useProjectSearch(query);

  const projects = query.trim().length > 0 ? searchResult.data ?? [] : data?.items ?? [];

  const domains = useMemo(() => Array.from(new Set((data?.items ?? []).map((project) => project.domain))), [data?.items]);
  const categories = useMemo(
    () => Array.from(new Set((data?.items ?? []).map((project) => project.ai_category).filter(Boolean) as string[])),
    [data?.items]
  );

  const filteredProjects = projects.filter((project) => {
    const matchesDomain = selectedDomain === 'all' || project.domain === selectedDomain;
    const matchesCategory = selectedCategory === 'all' || project.ai_category === selectedCategory;
    return matchesDomain && matchesCategory;
  });

  return (
    <main className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
      <div className="space-y-6">
        <ProjectFilter
          query={query}
          onQueryChange={setQuery}
          selectedDomain={selectedDomain}
          onDomainChange={setSelectedDomain}
          selectedCategory={selectedCategory}
          onCategoryChange={setSelectedCategory}
          domains={domains}
          categories={categories}
        />

        <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
          {filteredProjects.map((project) => (
            <ProjectCard key={project.id} project={project} />
          ))}
        </div>
      </div>
    </main>
  );
}
