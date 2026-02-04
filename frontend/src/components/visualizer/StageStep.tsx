import { cn } from '../../lib/utils';
import type { StageInfo } from '../../types/events';
import {
  Rocket,
  MessageSquare,
  Search,
  Database,
  History,
  Wrench,
  CheckCircle2,
  Play,
  AlertTriangle,
  Save,
  PartyPopper,
} from 'lucide-react';

interface StageStepProps {
  stage: StageInfo;
  isLast?: boolean;
}

const stageIcons: Record<string, any> = {
  initializing: Rocket,
  loading_conversation: MessageSquare,
  analyzing_intent: Search,
  retrieving_schema: Database,
  searching_history: History,
  generating_sql: Wrench,
  validating_sql: CheckCircle2,
  executing_query: Play,
  correcting_errors: AlertTriangle,
  saving_success: Save,
  completed: PartyPopper,
};

export const StageStep = ({ stage, isLast }: StageStepProps) => {
  const Icon = stageIcons[stage.stage] || Wrench;

  return (
    <div className="relative">
      <div className="flex items-start gap-3">
        {/* Icon */}
        <div
          className={cn(
            'w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 relative z-10',
            {
              'bg-accent text-white animate-pulse-soft': stage.status === 'active',
              'bg-success text-white': stage.status === 'completed',
              'bg-error text-white': stage.status === 'error',
              'bg-gray-600 text-gray-300': stage.status === 'pending',
            }
          )}
        >
          <Icon className="w-4 h-4" />
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0 pb-6">
          <p
            className={cn('text-sm font-medium capitalize', {
              'text-accent': stage.status === 'active',
              'text-success': stage.status === 'completed',
              'text-error': stage.status === 'error',
            })}
          >
            {stage.stage.replace(/_/g, ' ')}
          </p>
          <p className="text-xs text-muted mt-1">{stage.message}</p>
          {stage.timestamp && (
            <p className="text-xs text-muted mt-1">
              {new Date(stage.timestamp).toLocaleTimeString()}
            </p>
          )}
        </div>
      </div>

      {/* Connecting line */}
      {!isLast && (
        <div
          className={cn(
            'absolute left-4 top-8 w-0.5 h-full -translate-x-1/2',
            stage.status === 'completed'
              ? 'bg-success'
              : stage.status === 'error'
              ? 'bg-error'
              : 'bg-gray-600'
          )}
        />
      )}
    </div>
  );
};
