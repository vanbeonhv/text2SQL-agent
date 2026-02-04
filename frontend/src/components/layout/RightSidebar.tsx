import { useSidebarStore } from '../../stores/useSidebarStore';
import { CollapseToggle } from '../ui/CollapseToggle';
import { useProcessStore } from '../../stores/useProcessStore';
import { Activity } from 'lucide-react';
import { StageStep } from '../visualizer/StageStep';
import { IntentBadge } from '../visualizer/IntentBadge';
import { SchemaTree } from '../visualizer/SchemaTree';
import { SimilarExamplesCards } from '../visualizer/SimilarExamplesCards';
import { ValidationStatus } from '../visualizer/ValidationStatus';

export const RightSidebar = () => {
  const { rightExpanded, toggleRight } = useSidebarStore();
  const { stages, intent, schema, similarExamples, validation } = useProcessStore();

  if (!rightExpanded) {
    return (
      <aside className="relative h-full surface border-l border-default flex flex-col items-center py-4">
        <div className="w-10 h-10 rounded-lg flex items-center justify-center">
          <Activity className="w-5 h-5 text-muted" />
        </div>
        <CollapseToggle expanded={rightExpanded} onToggle={toggleRight} side="right" />
      </aside>
    );
  }

  return (
    <aside className="relative h-full surface border-l border-default flex flex-col overflow-hidden">
      <div className="p-4 border-b border-default">
        <h2 className="text-lg font-heading font-semibold flex items-center gap-2">
          <Activity className="w-5 h-5" />
          Process Visualizer
        </h2>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {stages.length === 0 ? (
          <div className="text-center text-muted py-8">
            <Activity className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p className="text-sm">No active process</p>
            <p className="text-xs mt-1">Send a message to see the process visualization</p>
          </div>
        ) : (
          <>
            {/* Stage Timeline */}
            <div className="space-y-0">
              {stages.map((stage, index) => (
                <StageStep 
                  key={index} 
                  stage={stage} 
                  isLast={index === stages.length - 1}
                />
              ))}
            </div>

            {/* Additional Details */}
            {intent && <IntentBadge intent={intent} />}
            {schema && <SchemaTree schema={schema} />}
            {similarExamples && <SimilarExamplesCards examples={similarExamples} />}
            {validation && <ValidationStatus validation={validation} />}
          </>
        )}
      </div>

      <CollapseToggle expanded={rightExpanded} onToggle={toggleRight} side="right" />
    </aside>
  );
};
