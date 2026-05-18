"use client";

import { useQuery } from '@tanstack/react-query';
import { searchApi } from '@/lib/api';

export function useSemanticSearch(query: string) {
  return useQuery({
    queryKey: ['semantic-search', query],
    queryFn: () => searchApi.semantic(query),
    enabled: query.trim().length > 0,
    staleTime: 15_000
  });
}

export function useHybridSearch(query: string) {
  return useQuery({
    queryKey: ['hybrid-search', query],
    queryFn: () => searchApi.hybrid(query),
    enabled: query.trim().length > 0,
    staleTime: 15_000
  });
}
