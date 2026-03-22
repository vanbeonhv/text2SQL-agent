import { create } from 'zustand';
import type { Message, ConversationMetadata } from '../types/chat';

interface ChatStore {
  activeConversationId: string | null;
  activeConversationMetadata: ConversationMetadata | null;
  messages: Message[];
  isStreaming: boolean;
  isLoadingHistory: boolean;

  setActiveConversation: (id: string | null) => void;
  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void;
  updateLastMessage: (updates: Partial<Message>) => void;
  setMessageFeedback: (messageId: string, feedback: 'like' | 'dislike' | null) => void;
  clearMessages: () => void;
  setIsStreaming: (isStreaming: boolean) => void;
  setMessages: (messages: Message[]) => void;
  setConversationMetadata: (metadata: ConversationMetadata | null) => void;
  setIsLoadingHistory: (isLoading: boolean) => void;
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

  setMessageFeedback: (messageId, feedback) => set((state) => ({
    messages: state.messages.map((m) =>
      m.id === messageId ? { ...m, feedback } : m
    ),
  })),

  clearMessages: () => set({
    messages: [],
    activeConversationId: null,
    activeConversationMetadata: null,
  }),

  setIsStreaming: (isStreaming) => set({ isStreaming }),

  setMessages: (messages) => set({ messages }),

  setConversationMetadata: (metadata) => set({ activeConversationMetadata: metadata }),

  setIsLoadingHistory: (isLoading) => set({ isLoadingHistory: isLoading }),
}));
