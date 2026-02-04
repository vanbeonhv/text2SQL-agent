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

export interface Conversation {
  id: string;
  title: string;
  created_at: number;
  updated_at: number;
  messages: Message[];
}
