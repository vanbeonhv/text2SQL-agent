import { MessageSquare, Loader } from 'lucide-react';
import { cn } from '../../lib/utils';
import type { ConversationListItem } from '../../types/api';

interface ConversationListProps {
  conversations: ConversationListItem[];
  isLoading: boolean;
  activeConversationId: string | null;
  isLoadingHistory: boolean;
  onSelectConversation: (conversationId: string) => void;
}

export const ConversationList: React.FC<ConversationListProps> = ({
  conversations,
  isLoading,
  activeConversationId,
  isLoadingHistory,
  onSelectConversation,
}) => {
  if (isLoading) {
    return (
      <div className="flex-1 overflow-y-auto px-2">
        <div className="p-4 flex items-center justify-center text-muted">
          <Loader className="w-4 h-4 animate-spin mr-2" />
          Loading conversations...
        </div>
      </div>
    );
  }

  if (conversations?.length === 0) {
    return (
      <div className="flex-1 overflow-y-auto px-2">
        <div className="p-4 text-center text-muted text-sm">
          No conversations yet
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto px-2">
      <div className="space-y-1">
        {conversations.map((conversation: ConversationListItem) => (
          <button
            key={conversation.id}
            onClick={() => onSelectConversation(conversation.id)}
            disabled={isLoadingHistory}
            className={cn(
              "w-full p-3 rounded-lg text-left transition-colors",
              "hover:bg-light-elevated dark:hover:bg-dark-elevated",
              "disabled:opacity-50 disabled:cursor-not-allowed",
              activeConversationId === conversation.id
                ? "bg-light-elevated dark:bg-dark-elevated"
                : ""
            )}
          >
            <div className="flex items-start gap-2">
              <MessageSquare className="w-4 h-4 mt-0.5 text-muted flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">
                  {conversation.title}
                </p>
                <p className="text-xs text-muted">
                  {new Date(conversation.updated_at).toLocaleDateString()}
                </p>
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
};
