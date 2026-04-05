export interface ChatRequest {
  question: string;
  conversation_id?: string;
}

export interface QueryResult {
  success?: boolean;
  rows: Array<Record<string, unknown>>;
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
  metadata?: Record<string, unknown>;
  feedback?: string | null;
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

export type ConversationListItem = ConversationMetadata;

export interface ConversationsListResponse {
  conversations: ConversationListItem[];
  count: number;
}

export interface HealthResponse {
  status: string;
  version: string;
}

export interface SchemaColumnDefinition {
  name: string;
  type: string;
  primary_key?: boolean;
  description?: string;
}

export interface SchemaRelationshipDefinition {
  from: string;
  to: string;
  type: string;
  [key: string]: unknown;
}

export interface SchemaTableDefinition {
  table_name: string;
  columns: SchemaColumnDefinition[];
  relationships: SchemaRelationshipDefinition[];
  description?: string | null;
  tags: string[];
  is_active: boolean;
}

export interface SchemaBusinessContextResponse {
  business_context: Record<string, unknown>;
  explicit: boolean;
}

export interface SchemaDetectRequest {
  question: string;
  active_only?: boolean;
  allow_llm_fallback?: boolean;
}

export interface SchemaDetectResponse {
  target_tables: string[];
  confidence: number;
  strategy: 'heuristic' | 'llm_fallback';
  matched_reasons: string[];
}

