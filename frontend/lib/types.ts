export interface TechStack {
  languages: string[];
  frameworks: string[];
  tools: string[];
}

export interface Project {
  id: string;
  name: string;
  description: string;
  domain: string;
  ai_category: string | null;
  tech_stack: TechStack;
  repo_url: string | null;
  is_active: boolean;
  created_at: string;
}

export interface ChatSource {
  project_id: string;
  project_name: string;
  chunk_type: string;
  content: string;
  score: number;
  metadata?: Record<string, unknown>;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  sources?: ChatSource[];
}

export interface ChatRequest {
  message: string;
  conversation_id?: string;
  user_id?: string;
}

export interface ChatResponse {
  response: string;
  conversation_id: string;
  sources: ChatSource[];
  message_id: string;
  timestamp: string;
}

export interface SearchResult {
  project_id: string;
  project_name: string;
  chunk_type: string;
  content: string;
  score: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface IndexingStatus {
  collections: Record<string, {
    name: string;
    vector_count: number;
    vectors_size: number;
    distance_metric: string;
  }>;
  status: string;
}

export interface ConversationHistoryResponse {
  conversation_id: string;
  messages: ChatMessage[];
  total: number;
}
