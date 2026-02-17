export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
  sql?: string;
  results?: QueryResult;
  error?: string;
}

export interface QueryResult {
  rows: Array<Record<string, any>>;
  count: number;
  columns?: string[];
}

export interface ConversationMetadata {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface Conversation extends ConversationMetadata {
  messages: Message[];
}

