import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';
import type { ConversationResponse } from '../types/api';

export const useConversation = (id: string | null) => {
  return useQuery<ConversationResponse>({
    queryKey: ['conversation', id],
    queryFn: () => {
      if (!id) throw new Error('No conversation ID');
      return api.getConversation(id);
    },
    enabled: !!id,
    staleTime: 30000, // 30 seconds
  });
};

// TODO: Add this endpoint to the backend
export const useConversations = () => {
  return useQuery({
    queryKey: ['conversations'],
    queryFn: async () => {
      // Placeholder - backend endpoint doesn't exist yet
      return [];
    },
    staleTime: 30000,
  });
};
