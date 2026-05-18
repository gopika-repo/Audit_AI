import axios, { AxiosError, AxiosInstance, AxiosResponse } from 'axios';
import type {
  ChatRequest,
  ChatResponse,
  ConversationHistoryResponse,
  IndexingStatus,
  PaginatedResponse,
  Project,
  SearchResult
} from '@/lib/types';

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

export function createAxiosInstance(): AxiosInstance {
  const instance = axios.create({
    baseURL: API_URL,
    timeout: 30000,
    headers: {
      'Content-Type': 'application/json'
    }
  });

  instance.interceptors.request.use((config) => {
    const method = config.method?.toUpperCase() ?? 'GET';
    const url = `${config.baseURL ?? ''}${config.url ?? ''}`;
    console.info(`[api] ${method} ${url}`);
    return config;
  });

  instance.interceptors.response.use(
    (response) => {
      console.info(`[api] ${response.status} ${response.config.url}`);
      return response;
    },
    (error: AxiosError<{ detail?: string }>) => {
      const message = error.response?.data?.detail ?? error.message ?? 'Request failed';
      console.error('[api] error', message);
      return Promise.reject(new Error(message));
    }
  );

  return instance;
}

const api = createAxiosInstance();

async function unwrap<T>(promise: Promise<AxiosResponse<T>>): Promise<T> {
  const response = await promise;
  return response.data;
}

export const projectsApi = {
  getAll: async (): Promise<PaginatedResponse<Project>> => unwrap(api.get('/api/v1/projects')),
  getById: async (id: string): Promise<Project> => unwrap(api.get(`/api/v1/projects/${id}`)),
  search: async (q: string): Promise<Project[]> => unwrap(api.get('/api/v1/projects/search', { params: { q } })),
  getByDomain: async (domain: string): Promise<PaginatedResponse<Project>> =>
    unwrap(api.get(`/api/v1/projects/domain/${encodeURIComponent(domain)}`))
};

export const chatApi = {
  sendMessage: async (payload: ChatRequest): Promise<ChatResponse> =>
    unwrap(api.post('/api/v1/chat/message', payload)),
  getHistory: async (conversationId: string): Promise<ConversationHistoryResponse> =>
    unwrap(api.get(`/api/v1/chat/history/${conversationId}`)),
  clearHistory: async (conversationId: string): Promise<{ status: string; conversation_id: string }> =>
    unwrap(api.delete(`/api/v1/chat/history/${conversationId}`))
};

export const indexingApi = {
  getStatus: async (): Promise<IndexingStatus> => unwrap(api.get('/api/v1/indexing/status')),
  indexAll: async (): Promise<{ indexed: number; failed: number; chunks_total: number; status: string }> =>
    unwrap(api.post('/api/v1/indexing/projects'))
};

export const searchApi = {
  semantic: async (query: string, limit = 5): Promise<{ query: string; results: SearchResult[]; total: number }> =>
    unwrap(api.post('/api/v1/search/semantic', { query, limit })),
  hybrid: async (query: string, limit = 5): Promise<{ query: string; results: SearchResult[]; total: number }> =>
    unwrap(api.post('/api/v1/search/hybrid', { query, limit }))
};
