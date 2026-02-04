import { Avatar } from '../ui/Avatar';

export const TypingIndicator = () => {
  return (
    <div className="flex gap-3 justify-start">
      <Avatar fallback="AI" size="sm" className="bg-accent" />
      <div className="surface elevated rounded-lg px-4 py-3">
        <div className="flex items-center gap-1">
          <div className="w-2 h-2 rounded-full bg-current animate-pulse" style={{ animationDelay: '0ms' }} />
          <div className="w-2 h-2 rounded-full bg-current animate-pulse" style={{ animationDelay: '150ms' }} />
          <div className="w-2 h-2 rounded-full bg-current animate-pulse" style={{ animationDelay: '300ms' }} />
        </div>
      </div>
    </div>
  );
};
