"use client";

import { useQuery } from '@tanstack/react-query';
import { projectsApi } from '@/lib/api';

export function useProjects() {
  return useQuery({
    queryKey: ['projects'],
    queryFn: projectsApi.getAll,
    staleTime: 60_000
  });
}

export function useProject(projectId: string) {
  return useQuery({
    queryKey: ['project', projectId],
    queryFn: () => projectsApi.getById(projectId),
    enabled: projectId.length > 0,
    staleTime: 60_000
  });
}

export function useProjectSearch(query: string) {
  return useQuery({
    queryKey: ['projects-search', query],
    queryFn: () => projectsApi.search(query),
    enabled: query.trim().length > 0,
    staleTime: 30_000
  });
}
