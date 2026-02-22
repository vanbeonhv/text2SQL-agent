export interface ChatRequest {
  question: string;
  conversation_id?: string;
}

export interface QueryResult {
  success?: boolean;
  rows: Array<Record<string, any>>;
  count: number;
  columns?: string[];
  error?: string;
}

export interface ConversationMessage {
  id: number;
  role: 'user' | 'assistant';
  content: string;
  sql?: string;
  results?: QueryResult;
  error?: string;
  metadata?: Record<string, any>;
  timestamp: string;
}

export interface ConversationMetadata {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface ConversationResponse extends ConversationMetadata {
  messages: ConversationMessage[];
}

export interface ConversationListItem extends ConversationMetadata {}

export interface ConversationsListResponse {
  conversations: ConversationListItem[];
  count: number;
}

export interface HealthResponse {
  status: string;
  version: string;
}

