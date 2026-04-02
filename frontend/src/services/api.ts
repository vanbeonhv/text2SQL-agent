import type {
  ConversationResponse,
  ConversationsListResponse,
  HealthResponse,
  SchemaDetectRequest,
  SchemaDetectResponse,
  SchemaTableDefinition,
} from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = {
  baseURL: API_BASE_URL,
  
  async streamChat(question: string, conversationId?: string): Promise<Response> {
    const response = await fetch(`${API_BASE_URL}/api/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        question,
        conversation_id: conversationId,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response;
  },

  async getConversation(id: string): Promise<ConversationResponse> {
    const response = await fetch(`${API_BASE_URL}/api/conversations/${id}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  },

  async getConversations(): Promise<ConversationsListResponse> {
    const response = await fetch(`${API_BASE_URL}/api/conversations`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  },

  async healthCheck(): Promise<HealthResponse> {
    const response = await fetch(`${API_BASE_URL}/api/health`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  },

  async submitFeedback(
    sql: string,
    status: 'like' | 'dislike' | 'none',
    conversationId: string,
  ): Promise<{ status: string; message: string }> {
    const response = await fetch(`${API_BASE_URL}/api/feedback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sql, status, conversation_id: conversationId }),
    });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  },

  async listSchemaTables(activeOnly: boolean = true): Promise<SchemaTableDefinition[]> {
    const url = new URL(`${API_BASE_URL}/api/schema/tables`);
    url.searchParams.set('active_only', String(activeOnly));
    const response = await fetch(url.toString());
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return response.json();
  },

  async getSchemaTable(tableName: string): Promise<SchemaTableDefinition> {
    const response = await fetch(`${API_BASE_URL}/api/schema/tables/${encodeURIComponent(tableName)}`);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return response.json();
  },

  async upsertSchemaTable(payload: SchemaTableDefinition): Promise<SchemaTableDefinition> {
    const response = await fetch(`${API_BASE_URL}/api/schema/tables`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return response.json();
  },

  async updateSchemaTable(tableName: string, payload: SchemaTableDefinition): Promise<SchemaTableDefinition> {
    const response = await fetch(`${API_BASE_URL}/api/schema/tables/${encodeURIComponent(tableName)}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return response.json();
  },

  async deleteSchemaTable(tableName: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/schema/tables/${encodeURIComponent(tableName)}`, {
      method: 'DELETE',
    });
    if (!response.ok && response.status !== 204) throw new Error(`HTTP error! status: ${response.status}`);
  },

  async detectSchemaTables(payload: SchemaDetectRequest): Promise<SchemaDetectResponse> {
    const response = await fetch(`${API_BASE_URL}/api/schema/detect`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return response.json();
  },
};
