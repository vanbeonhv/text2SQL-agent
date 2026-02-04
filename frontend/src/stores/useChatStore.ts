import { create } from 'zustand';
import type { Message } from '../types/chat';

interface ChatStore {
  activeConversationId: string | null;
  messages: Message[];
  isStreaming: boolean;
  
  setActiveConversation: (id: string | null) => void;
  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void;
  updateLastMessage: (updates: Partial<Message>) => void;
  clearMessages: () => void;
  setIsStreaming: (isStreaming: boolean) => void;
  setMessages: (messages: Message[]) => void;
}

export const useChatStore = create<ChatStore>((set) => ({
  activeConversationId: null,
  messages: [],
  isStreaming: false,
  
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
      messages[messages.length - 1] = {
        ...messages[messages.length - 1],
        ...updates,
      };
    }
    return { messages };
  }),
  
  clearMessages: () => set({ messages: [] }),
  
  setIsStreaming: (isStreaming) => set({ isStreaming }),
  
  setMessages: (messages) => set({ messages }),
}));
