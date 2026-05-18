"use client";

import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';

export function ProjectFilter({
  query,
  onQueryChange,
  selectedDomain,
  onDomainChange,
  selectedCategory,
  onCategoryChange,
  domains,
  categories
}: {
  query: string;
  onQueryChange: (value: string) => void;
  selectedDomain: string;
  onDomainChange: (value: string) => void;
  selectedCategory: string;
  onCategoryChange: (value: string) => void;
  domains: string[];
  categories: string[];
}) {
  return (
    <div className="space-y-4 rounded-3xl border border-white/10 bg-white/5 p-5 backdrop-blur-xl">
      <Input
        value={query}
        onChange={(event) => onQueryChange(event.target.value)}
        placeholder="Search projects by name, description, or domain..."
        aria-label="Search projects"
      />

      <div className="flex flex-wrap gap-2">
        <Badge tone={selectedDomain === 'all' ? 'default' : 'muted'} className="cursor-pointer" onClick={() => onDomainChange('all')}>
          All domains
        </Badge>
        {domains.map((domain) => (
          <Badge
            key={domain}
            tone={selectedDomain === domain ? 'default' : 'muted'}
            className="cursor-pointer"
            onClick={() => onDomainChange(domain)}
          >
            {domain}
          </Badge>
        ))}
      </div>

      <div className="flex flex-wrap gap-2">
        <Badge tone={selectedCategory === 'all' ? 'default' : 'muted'} className="cursor-pointer" onClick={() => onCategoryChange('all')}>
          All categories
        </Badge>
        {categories.map((category) => (
          <Badge
            key={category}
            tone={selectedCategory === category ? 'default' : 'muted'}
            className="cursor-pointer"
            onClick={() => onCategoryChange(category)}
          >
            {category}
          </Badge>
        ))}
      </div>
    </div>
  );
}
