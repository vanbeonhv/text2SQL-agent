export interface ChatRequest {
  question: string;
  conversation_id?: string;
}

export interface ConversationMessage {
  role: 'user' | 'assistant';
  content: string;
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

