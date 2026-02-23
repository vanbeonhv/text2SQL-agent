import { Avatar } from '../ui/Avatar';
import type { Message } from '../../types/chat';

interface UserMessageProps {
  message: Message;
}

export const UserMessage = ({ message }: UserMessageProps) => {
  return (
    <div className="flex gap-3 justify-end">
      <div className="max-w-[80%] surface elevated rounded-lg px-4 py-3">
        <p className="text-sm whitespace-pre-wrap wrap-break-word">
          {message.content}
        </p>
      </div>
      <Avatar fallback="U" size="sm" />
    </div>
  );
};
