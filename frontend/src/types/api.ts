export interface ChatRequest {
  question: string;
  conversation_id?: string;
}

export interface ConversationResponse {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  messages: Array<{
    role: string;
    content: string;
    timestamp: string;
  }>;
}

export interface HealthResponse {
  status: string;
  version: string;
}
