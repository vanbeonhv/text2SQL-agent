import { Database, Table2, ChevronDown, ChevronRight } from 'lucide-react';
import { useState } from 'react';
import type { SchemaEvent } from '../../types/events';

interface SchemaTreeProps {
  schema: SchemaEvent;
}

export const SchemaTree = ({ schema }: SchemaTreeProps) => {
  const [expandedTables, setExpandedTables] = useState<Set<string>>(new Set());

  const toggleTable = (tableName: string) => {
    const newExpanded = new Set(expandedTables);
    if (newExpanded.has(tableName)) {
      newExpanded.delete(tableName);
    } else {
      newExpanded.add(tableName);
    }
    setExpandedTables(newExpanded);
  };

  return (
    <div className="surface elevated rounded-lg p-4 border border-default">
      <div className="flex items-center gap-2 mb-3">
        <Database className="w-4 h-4 text-primary" />
        <h3 className="text-sm font-medium">Database Schema</h3>
      </div>

      <div className="space-y-2">
        {schema.tables.map((table: any, idx: number) => {
          const tableName = table.name || table.table_name || `Table ${idx + 1}`;
          const columns = table.columns || [];
          const isExpanded = expandedTables.has(tableName);

          return (
            <div key={idx} className="border border-default rounded-lg overflow-hidden">
              <button
                onClick={() => toggleTable(tableName)}
                className="w-full px-3 py-2 flex items-center gap-2 hover:bg-light-elevated dark:hover:bg-dark-elevated transition-colors cursor-pointer"
              >
                {isExpanded ? (
                  <ChevronDown className="w-4 h-4 text-muted" />
                ) : (
                  <ChevronRight className="w-4 h-4 text-muted" />
                )}
                <Table2 className="w-4 h-4 text-accent" />
                <span className="text-sm font-medium font-code">{tableName}</span>
                <span className="text-xs text-muted ml-auto">
                  {columns.length} columns
                </span>
              </button>

              {isExpanded && columns.length > 0 && (
                <div className="border-t border-default bg-light-elevated/50 dark:bg-dark-elevated/50">
                  <div className="px-3 py-2 space-y-1">
                    {columns.map((col: any, colIdx: number) => (
                      <div
                        key={colIdx}
                        className="flex items-center gap-2 text-xs py-1"
                      >
                        <div className="w-1.5 h-1.5 rounded-full bg-primary" />
                        <span className="font-code font-medium">
                          {col.name || col.column_name}
                        </span>
                        <span className="text-muted">
                          {col.type || col.data_type}
                        </span>
                        {col.primary_key && (
                          <span className="text-xs px-1.5 py-0.5 rounded bg-primary/20 text-primary">
                            PK
                          </span>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
