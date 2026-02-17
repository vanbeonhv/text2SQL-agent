import { useSidebarStore } from '../../stores/useSidebarStore';
import { useChatStore } from '../../stores/useChatStore';
import { useConversations } from '../../hooks/useConversations';
import { CollapseToggle } from '../ui/CollapseToggle';
import { CollapsedSidebar } from './CollapsedSidebar';
import { ConversationList } from './ConversationList';
import { cn } from '../../lib/utils';
import { Plus } from 'lucide-react';
import { Button } from '../ui/Button';

export const LeftSidebar = () => {
  const { leftExpanded, toggleLeft } = useSidebarStore();
  const { activeConversationId, loadConversationHistory, isLoadingHistory } = useChatStore();
  const { conversations, isLoading } = useConversations();

  const handleNewChat = (): void => {
    // Clear current conversation
    useChatStore.setState({ 
      activeConversationId: null,
      messages: [],
      activeConversationMetadata: null,
    });
  };

  const handleSelectConversation = async (conversationId: string): Promise<void> => {
    try {
      await loadConversationHistory(conversationId);
    } catch (error) {
      console.error('Failed to load conversation:', error);
    }
  };

  if (!leftExpanded) {
    return (
      <CollapsedSidebar
        onNewChat={handleNewChat}
        leftExpanded={leftExpanded}
        onToggleLeft={toggleLeft}
      />
    );
  }

  return (
    <aside className="relative h-full surface border-r border-default flex flex-col">
      <div className="p-4 space-y-4">
        <Button
          className="w-full justify-start gap-2"
          variant="primary"
          onClick={handleNewChat}
        >
          <Plus className="w-4 h-4" />
          New Chat
        </Button>

        <div className="relative">
          <input
            type="text"
            placeholder="Search conversations..."
            className={cn(
              "w-full pl-10 pr-4 py-2 rounded-lg",
              "surface elevated border border-default",
              "focus:outline-none focus:ring-2 focus:ring-primary",
              "placeholder:text-muted"
            )}
          />
        </div>
      </div>

      <ConversationList
        conversations={conversations}
        isLoading={isLoading}
        activeConversationId={activeConversationId}
        isLoadingHistory={isLoadingHistory}
        onSelectConversation={handleSelectConversation}
      />

      <CollapseToggle expanded={leftExpanded} onToggle={toggleLeft} side="left" />
    </aside>
  );
};
