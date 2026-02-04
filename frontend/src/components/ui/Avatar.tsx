import { cn } from '../../lib/utils';
import { User } from 'lucide-react';

interface AvatarProps {
  src?: string;
  alt?: string;
  fallback?: string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export const Avatar = ({ src, alt, fallback, size = 'md', className }: AvatarProps) => {
  const sizeClasses = {
    sm: 'w-8 h-8 text-xs',
    md: 'w-10 h-10 text-sm',
    lg: 'w-12 h-12 text-base',
  };

  if (src) {
    return (
      <img
        src={src}
        alt={alt || 'Avatar'}
        className={cn(
          'rounded-full object-cover',
          sizeClasses[size],
          className
        )}
      />
    );
  }

  return (
    <div
      className={cn(
        'rounded-full bg-primary text-white flex items-center justify-center font-medium',
        sizeClasses[size],
        className
      )}
    >
      {fallback ? (
        fallback.charAt(0).toUpperCase()
      ) : (
        <User className="w-1/2 h-1/2" />
      )}
    </div>
  );
};
