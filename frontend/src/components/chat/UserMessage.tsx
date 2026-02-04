import { Avatar } from '../ui/Avatar';
import type { Message } from '../../types/chat';

interface UserMessageProps {
  message: Message;
}

export const UserMessage = ({ message }: UserMessageProps) => {
  return (
    <div className="flex gap-3 justify-end">
      <div className="max-w-[80%] rounded-lg px-4 py-3 bg-primary text-white">
        <p className="text-sm whitespace-pre-wrap">{message.content}</p>
      </div>
      <Avatar fallback="U" size="sm" />
    </div>
  );
};
