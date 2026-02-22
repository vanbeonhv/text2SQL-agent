// SSE Event types matching backend
export interface StageEvent {
  stage: string;
  message: string;
  icon?: string;
}

export interface ConversationIdEvent {
  conversation_id: string;
}

export interface IntentEvent {
  intent: string;
  details?: Record<string, any>;
}

export interface SchemaEvent {
  tables: Array<Record<string, any>>;
  relationships?: Array<Record<string, any>>;
}

export interface SimilarExamplesEvent {
  count: number;
  examples: Array<Record<string, any>>;
}

export interface SQLEvent {
  sql: string;
  explanation?: string;
}

export interface ValidationEvent {
  valid: boolean;
  errors?: string[];
}

export interface ResultEvent {
  rows: Array<Record<string, any>>;
  count: number;
  columns?: string[];
}

export interface ErrorEvent {
  error: string;
  retry_count?: number;
}

export interface FormattedResponseEvent {
  markdown: string;
  format_method: string;
  has_llm_summary: boolean;
}

export interface CompleteEvent {
  success: boolean;
  message?: string;
}

export type SSEEvent =
  | { type: 'conversation_id'; data: ConversationIdEvent }
  | { type: 'stage'; data: StageEvent }
  | { type: 'intent'; data: IntentEvent }
  | { type: 'schema'; data: SchemaEvent }
  | { type: 'similar_examples'; data: SimilarExamplesEvent }
  | { type: 'sql'; data: SQLEvent }
  | { type: 'validation'; data: ValidationEvent }
  | { type: 'result'; data: ResultEvent }
  | { type: 'error'; data: ErrorEvent }
  | { type: 'formatted_response'; data: FormattedResponseEvent }
  | { type: 'complete'; data: CompleteEvent };

export type StageStatus = 'pending' | 'active' | 'completed' | 'error';

export interface StageInfo {
  stage: string;
  message: string;
  icon?: string;
  status: StageStatus;
  timestamp?: number;
}
