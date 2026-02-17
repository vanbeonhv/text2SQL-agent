import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';
import type { ConversationResponse, ConversationListItem, ConversationsListResponse } from '../types/api';

interface UseConversationResult {
  data: ConversationResponse | undefined;
  isLoading: boolean;
  error: Error | null;
  isError: boolean;
}

interface UseConversationsResult {
  conversations: ConversationListItem[];
  isLoading: boolean;
  error: Error | null;
  isError: boolean;
  refetch: () => Promise<any>;
}

export const useConversation = (id: string | null): UseConversationResult => {
  const { data, isLoading, error, isError } = useQuery<ConversationResponse>({
    queryKey: ['conversation', id],
    queryFn: () => {
      if (!id) throw new Error('No conversation ID');
      return api.getConversation(id);
    },
    enabled: !!id,
    staleTime: 30000, // 30 seconds
  });

  return {
    data,
    isLoading,
    error: error as Error | null,
    isError,
  };
};

export const useConversations = (): UseConversationsResult => {
  const { data, isLoading, error, isError, refetch } = useQuery<ConversationsListResponse>({
    queryKey: ['conversations'],
    queryFn: () => api.getConversations(),
    staleTime: 30000, // 30 seconds
  });

  return {
    conversations: data?.conversations ?? [],
    isLoading,
    error: error as Error | null,
    isError,
    refetch,
  };
};

