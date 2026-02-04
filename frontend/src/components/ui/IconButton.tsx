import { forwardRef } from 'react';
import type { ButtonHTMLAttributes } from 'react';
import { cn } from '../../lib/utils';

interface IconButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'ghost' | 'primary' | 'secondary';
  size?: 'sm' | 'md' | 'lg';
}

export const IconButton = forwardRef<HTMLButtonElement, IconButtonProps>(
  ({ className, variant = 'ghost', size = 'md', children, ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={cn(
          'inline-flex items-center justify-center rounded-lg transition-colors cursor-pointer',
          'focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2',
          'disabled:opacity-50 disabled:cursor-not-allowed',
          {
            'hover:bg-light-elevated dark:hover:bg-dark-elevated': variant === 'ghost',
            'bg-primary text-white hover:bg-primary-700': variant === 'primary',
            'bg-accent text-white hover:bg-accent-600': variant === 'secondary',
          },
          {
            'w-8 h-8 text-sm': size === 'sm',
            'w-10 h-10 text-base': size === 'md',
            'w-12 h-12 text-lg': size === 'lg',
          },
          className
        )}
        {...props}
      >
        {children}
      </button>
    );
  }
);

IconButton.displayName = 'IconButton';
