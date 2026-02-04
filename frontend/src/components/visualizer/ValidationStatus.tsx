import { CheckCircle2, XCircle, AlertCircle } from 'lucide-react';
import type { ValidationEvent } from '../../types/events';

interface ValidationStatusProps {
  validation: ValidationEvent;
}

export const ValidationStatus = ({ validation }: ValidationStatusProps) => {
  return (
    <div className="surface elevated rounded-lg p-4 border border-default">
      <div className="flex items-center gap-2 mb-3">
        {validation.valid ? (
          <CheckCircle2 className="w-4 h-4 text-success" />
        ) : (
          <XCircle className="w-4 h-4 text-error" />
        )}
        <h3 className="text-sm font-medium">SQL Validation</h3>
      </div>

      {validation.valid ? (
        <div className="flex items-center gap-2 text-success">
          <CheckCircle2 className="w-4 h-4" />
          <span className="text-sm">Query passed all validation checks</span>
        </div>
      ) : (
        <div className="space-y-2">
          <div className="flex items-start gap-2 text-error">
            <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
            <div className="flex-1">
              <p className="text-sm font-medium">Validation failed</p>
              {validation.errors && validation.errors.length > 0 && (
                <ul className="mt-2 space-y-1">
                  {validation.errors.map((error, idx) => (
                    <li key={idx} className="text-xs text-muted">
                      • {error}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
