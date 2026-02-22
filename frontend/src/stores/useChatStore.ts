import { create } from 'zustand';
import { api } from '../services/api';
import type { Message, ConversationMetadata } from '../types/chat';
import type { ConversationResponse } from '../types/api';

interface ChatStore {
  activeConversationId: string | null;
  activeConversationMetadata: ConversationMetadata | null;
  messages: Message[];
  isStreaming: boolean;
  isLoadingHistory: boolean;
  
  setActiveConversation: (id: string | null) => void;
  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void;
  updateLastMessage: (updates: Partial<Message>) => void;
  clearMessages: () => void;
  setIsStreaming: (isStreaming: boolean) => void;
  setMessages: (messages: Message[]) => void;
  setConversationMetadata: (metadata: ConversationMetadata | null) => void;
  loadConversationHistory: (conversationId: string) => Promise<void>;
}

export const useChatStore = create<ChatStore>((set) => ({
  activeConversationId: null,
  activeConversationMetadata: null,
  messages: [],
  isStreaming: false,
  isLoadingHistory: false,
  
  setActiveConversation: (id) => set({ activeConversationId: id }),
  
  addMessage: (message) => set((state) => ({
    messages: [
      ...state.messages,
      {
        ...message,
        id: crypto.randomUUID(),
        timestamp: Date.now(),
      },
    ],
  })),
  
  updateLastMessage: (updates) => set((state) => {
    const messages = [...state.messages];
    if (messages.length > 0) {
      const lastMessage = messages.at(-1);
      if (lastMessage) {
        messages[messages.length - 1] = {
          ...lastMessage,
          ...updates,
        };
      }
    }
    return { messages };
  }),
  
  clearMessages: () => set({ 
    messages: [],
    activeConversationId: null,
    activeConversationMetadata: null,
  }),
  
  setIsStreaming: (isStreaming) => set({ isStreaming }),
  
  setMessages: (messages) => set({ messages }),

  setConversationMetadata: (metadata) => set({ activeConversationMetadata: metadata }),

  loadConversationHistory: async (conversationId: string) => {
    set({ isLoadingHistory: true });
    try {
      const conversation: ConversationResponse = await api.getConversation(conversationId);
      
      // Convert API messages to store format
      const messages: Message[] = conversation.messages.map((msg) => ({
        id: `${conversation.id}-${msg.id}`,
        role: msg.role,
        content: msg.content,
        sql: msg.sql,
        results: msg.results,
        error: msg.error,
        metadata: msg.metadata,
        timestamp: new Date(msg.timestamp).getTime(),
      }));
      
      // Extract metadata
      const metadata: ConversationMetadata = {
        id: conversation.id,
        title: conversation.title,
        created_at: conversation.created_at,
        updated_at: conversation.updated_at,
      };

      set({ 
        messages,
        activeConversationId: conversationId,
        activeConversationMetadata: metadata,
      });
    } catch (error) {
      console.error('Failed to load conversation history:', error);
      throw error;
    } finally {
      set({ isLoadingHistory: false });
    }
  },

}));
