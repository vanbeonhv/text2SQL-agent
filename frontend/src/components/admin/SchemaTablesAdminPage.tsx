import { useEffect, useMemo, useState } from 'react';
import { Plus, Search, Save, Trash2 } from 'lucide-react';
import { Button } from '../ui/Button';
import { cn } from '../../lib/utils';
import type { SchemaColumnDefinition, SchemaRelationshipDefinition, SchemaTableDefinition } from '../../types/api';
import {
  useDeleteSchemaTable,
  useSchemaBusinessContext,
  useSchemaTables,
  useUpdateSchemaBusinessContext,
  useUpdateSchemaTable,
  useUpsertSchemaTable,
} from '../../hooks/useSchemaRegistry';

const EMPTY_DEF: SchemaTableDefinition = {
  table_name: '',
  description: '',
  tags: [],
  is_active: true,
  columns: [],
  relationships: [],
};

function parseJsonOrThrow<T>(value: string, label: string): T {
  try {
    return JSON.parse(value) as T;
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    throw new Error(`${label} is not valid JSON: ${msg}`);
  }
}

export const SchemaTablesAdminPage = () => {
  const [activeOnly, setActiveOnly] = useState(true);
  const [query, setQuery] = useState('');
  const [selected, setSelected] = useState<string | null>(null);
  const [mode, setMode] = useState<'create' | 'edit'>('edit');
  const [form, setForm] = useState<SchemaTableDefinition>(EMPTY_DEF);
  const [columnsJson, setColumnsJson] = useState('[]');
  const [relationshipsJson, setRelationshipsJson] = useState('[]');
  const [tagsText, setTagsText] = useState('');
  const [localError, setLocalError] = useState<string | null>(null);
  const [businessContextJson, setBusinessContextJson] = useState('{}');
  const [businessContextError, setBusinessContextError] = useState<string | null>(null);

  const tablesQuery = useSchemaTables(activeOnly);
  const businessContextQuery = useSchemaBusinessContext();
  const upsert = useUpsertSchemaTable();
  const update = useUpdateSchemaTable();
  const del = useDeleteSchemaTable();
  const updateBusinessContext = useUpdateSchemaBusinessContext();

  const editorTitle = useMemo(() => {
    if (mode === 'create') return 'Create table definition';
    return selected ?? 'Select a table';
  }, [mode, selected]);

  const items = useMemo(() => {
    const all = tablesQuery.data ?? [];
    const q = query.trim().toLowerCase();
    if (!q) return all;
    return all.filter((t) => t.table_name.toLowerCase().includes(q));
  }, [tablesQuery.data, query]);

  const listBody = useMemo(() => {
    if (tablesQuery.isLoading) return <div className="p-4 text-sm text-muted">Loading...</div>;
    if (tablesQuery.isError) return <div className="p-4 text-sm text-error">Failed to load schema tables</div>;
    if (items.length === 0) return <div className="p-4 text-sm text-muted">No tables found.</div>;
    return (
      <div className="p-2 space-y-1">
        {items.map((t) => (
          <button
            key={t.table_name}
            onClick={() => startEdit(t.table_name)}
            className={cn(
              'w-full text-left px-3 py-2 rounded-lg transition-colors cursor-pointer',
              'hover:bg-light-elevated dark:hover:bg-dark-elevated',
              selected === t.table_name && mode === 'edit' && 'bg-light-elevated dark:bg-dark-elevated',
            )}
          >
            <div className="flex items-center justify-between gap-2">
              <span className="text-sm font-code font-medium">{t.table_name}</span>
              {!t.is_active && (
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-warning/20 text-warning">
                  inactive
                </span>
              )}
            </div>
            <div className="text-xs text-muted mt-0.5 line-clamp-1">
              {t.description || '—'}
            </div>
          </button>
        ))}
      </div>
    );
  }, [items, mode, selected, tablesQuery.isError, tablesQuery.isLoading]);

  useEffect(() => {
    if (!tablesQuery.data) return;
    if (mode === 'create') return;
    if (!selected) {
      const first = items[0]?.table_name ?? null;
      setSelected(first);
      return;
    }
    const match = tablesQuery.data.find((t) => t.table_name === selected);
    if (!match) return;
    setForm(match);
    setColumnsJson(JSON.stringify(match.columns ?? [], null, 2));
    setRelationshipsJson(JSON.stringify(match.relationships ?? [], null, 2));
    setTagsText((match.tags ?? []).join(', '));
  }, [tablesQuery.data, items, mode, selected]);

  useEffect(() => {
    if (!businessContextQuery.data) return;
    setBusinessContextJson(JSON.stringify(businessContextQuery.data.business_context ?? {}, null, 2));
    setBusinessContextError(null);
  }, [businessContextQuery.data]);

  const saveBusinessContext = async () => {
    setBusinessContextError(null);
    try {
      const parsed = parseJsonOrThrow<unknown>(businessContextJson, 'business_context');
      if (parsed === null || typeof parsed !== 'object' || Array.isArray(parsed)) {
        throw new Error('business_context must be a JSON object (not an array or primitive)');
      }
      await updateBusinessContext.mutateAsync(parsed as Record<string, unknown>);
    } catch (e) {
      setBusinessContextError(e instanceof Error ? e.message : String(e));
    }
  };

  const startCreate = () => {
    setMode('create');
    setSelected(null);
    setLocalError(null);
    setForm(EMPTY_DEF);
    setColumnsJson('[]');
    setRelationshipsJson('[]');
    setTagsText('');
  };

  const startEdit = (tableName: string) => {
    setMode('edit');
    setSelected(tableName);
    setLocalError(null);
  };

  const save = async () => {
    setLocalError(null);
    try {
      const tags = tagsText
        .split(',')
        .map((x) => x.trim())
        .filter(Boolean);
      const columns = parseJsonOrThrow<SchemaColumnDefinition[]>(columnsJson, 'Columns');
      const relationships = parseJsonOrThrow<SchemaRelationshipDefinition[]>(relationshipsJson, 'Relationships');
      const payload: SchemaTableDefinition = {
        ...form,
        tags,
        columns,
        relationships,
      };

      if (!payload.table_name.trim()) throw new Error('Table name is required');

      if (mode === 'create') {
        const created = await upsert.mutateAsync(payload);
        setMode('edit');
        setSelected(created.table_name);
      } else {
        if (!selected) throw new Error('No table selected');
        await update.mutateAsync({ tableName: selected, payload });
      }
    } catch (e) {
      setLocalError(e instanceof Error ? e.message : String(e));
    }
  };

  const softDelete = async () => {
    if (!selected) return;
    setLocalError(null);
    try {
      await del.mutateAsync(selected);
      setSelected(null);
    } catch (e) {
      setLocalError(e instanceof Error ? e.message : String(e));
    }
  };

  return (
    <div className="h-full min-h-0 p-4 md:p-6">
      <div className="max-w-6xl mx-auto space-y-4">
        <div className="flex items-start justify-between gap-3">
          <div>
            <h1 className="text-xl md:text-2xl font-heading font-semibold">Schema &amp; Tables</h1>
            <p className="text-sm text-muted mt-1">Manage table-level schema definitions in `history.db`</p>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="secondary" onClick={startCreate} className="gap-2">
              <Plus className="w-4 h-4" />
              New table
            </Button>
            <Button variant="primary" onClick={save} className="gap-2" disabled={upsert.isPending || update.isPending}>
              <Save className="w-4 h-4" />
              Save
            </Button>
          </div>
        </div>

        {localError && (
          <div className="rounded-lg border border-error/30 bg-error/10 px-4 py-3 text-sm text-error">
            {localError}
          </div>
        )}

        <section className="surface border border-default rounded-xl overflow-hidden">
          <div className="p-4 border-b border-default flex flex-wrap items-center justify-between gap-3">
            <div>
              <div className="text-sm font-medium">business_context (registry)</div>
              <div className="text-xs text-muted mt-0.5">
                JSON object merged into LLM schema text when using registered tables. If never saved, the app falls
                back to <span className="font-code">backend/data/schema.json</span> business_context.
              </div>
            </div>
            <Button
              variant="secondary"
              onClick={saveBusinessContext}
              className="gap-2 shrink-0"
              disabled={updateBusinessContext.isPending || businessContextQuery.isLoading}
            >
              <Save className="w-4 h-4" />
              Save business context
            </Button>
          </div>
          <div className="p-4 space-y-2">
            {businessContextQuery.isError && (
              <div className="text-sm text-error">Failed to load business_context</div>
            )}
            {businessContextError && (
              <div className="rounded-lg border border-error/30 bg-error/10 px-3 py-2 text-sm text-error">
                {businessContextError}
              </div>
            )}
            <label htmlFor="schemaBusinessContextJson" className="text-xs text-muted sr-only">
              business_context JSON
            </label>
            <textarea
              id="schemaBusinessContextJson"
              value={businessContextJson}
              onChange={(e) => setBusinessContextJson(e.target.value)}
              className={cn(
                'w-full min-h-40 px-3 py-2 rounded-lg resize-y',
                'surface elevated border border-default',
                'focus:outline-none focus:ring-2 focus:ring-primary',
                'placeholder:text-muted text-xs font-code',
              )}
              spellCheck={false}
              placeholder='e.g. { "employment_status": "...", "query_notes": "..." }'
              disabled={businessContextQuery.isLoading}
            />
            {businessContextQuery.data && (
              <div className="text-xs text-muted">
                Stored in DB: {businessContextQuery.data.explicit ? 'yes (explicit)' : 'no (file fallback until you save)'}
              </div>
            )}
          </div>
        </section>

        <div className="grid grid-cols-1 md:grid-cols-[320px_1fr] gap-4 min-h-[70vh]">
          {/* List panel */}
          <section className="surface border border-default rounded-xl overflow-hidden flex flex-col min-h-0">
            <div className="p-3 border-b border-default space-y-2">
              <div className="relative">
                <Search className="w-4 h-4 text-muted absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  id="schemaTablesSearch"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Search table_name..."
                  className={cn(
                    'w-full pl-9 pr-3 py-2 rounded-lg',
                    'surface elevated border border-default',
                    'focus:outline-none focus:ring-2 focus:ring-primary',
                    'placeholder:text-muted text-sm'
                  )}
                />
              </div>
              <label className="flex items-center gap-2 text-xs text-muted">
                <input
                  id="schemaTablesActiveOnly"
                  type="checkbox"
                  checked={activeOnly}
                  onChange={(e) => setActiveOnly(e.target.checked)}
                />
                <span>Active only</span>
              </label>
            </div>

            <div className="flex-1 min-h-0 overflow-y-auto">
              {listBody}
            </div>
          </section>

          {/* Editor panel */}
          <section className="surface border border-default rounded-xl overflow-hidden flex flex-col min-h-0">
            <div className="p-4 border-b border-default flex items-center justify-between gap-3">
              <div>
                <div className="text-sm font-medium">{editorTitle}</div>
                <div className="text-xs text-muted mt-0.5">POST/PUT `/api/schema/tables`</div>
              </div>
              {mode === 'edit' && selected && (
                <Button variant="danger" size="sm" onClick={softDelete} className="gap-2" disabled={del.isPending}>
                  <Trash2 className="w-4 h-4" />
                  Delete
                </Button>
              )}
            </div>

            <div className="flex-1 min-h-0 overflow-y-auto p-4 space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label htmlFor="schemaTableName" className="text-xs text-muted">
                    table_name
                  </label>
                  <input
                    id="schemaTableName"
                    value={form.table_name}
                    onChange={(e) => setForm((p) => ({ ...p, table_name: e.target.value }))}
                    disabled={mode === 'edit'}
                    className={cn(
                      'w-full px-3 py-2 rounded-lg',
                      'surface elevated border border-default',
                      'focus:outline-none focus:ring-2 focus:ring-primary',
                      'placeholder:text-muted text-sm font-code',
                      mode === 'edit' && 'opacity-70'
                    )}
                    placeholder="e.g. products"
                  />
                </div>

                <div className="space-y-1">
                  <label htmlFor="schemaIsActive" className="text-xs text-muted">
                    is_active
                  </label>
                  <label className="flex items-center gap-2 text-sm" htmlFor="schemaIsActive">
                    <input
                      id="schemaIsActive"
                      type="checkbox"
                      checked={form.is_active}
                      onChange={(e) => setForm((p) => ({ ...p, is_active: e.target.checked }))}
                    />
                    <span>Active</span>
                  </label>
                </div>
              </div>

              <div className="space-y-1">
                <label htmlFor="schemaDescription" className="text-xs text-muted">
                  description
                </label>
                <input
                  id="schemaDescription"
                  value={form.description ?? ''}
                  onChange={(e) => setForm((p) => ({ ...p, description: e.target.value }))}
                  className={cn(
                    'w-full px-3 py-2 rounded-lg',
                    'surface elevated border border-default',
                    'focus:outline-none focus:ring-2 focus:ring-primary',
                    'placeholder:text-muted text-sm'
                  )}
                  placeholder="Human-friendly description"
                />
              </div>

              <div className="space-y-1">
                <label htmlFor="schemaTags" className="text-xs text-muted">
                  tags (comma-separated)
                </label>
                <input
                  id="schemaTags"
                  value={tagsText}
                  onChange={(e) => setTagsText(e.target.value)}
                  className={cn(
                    'w-full px-3 py-2 rounded-lg',
                    'surface elevated border border-default',
                    'focus:outline-none focus:ring-2 focus:ring-primary',
                    'placeholder:text-muted text-sm'
                  )}
                  placeholder="e.g. catalog, hr, finance"
                />
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label htmlFor="schemaColumnsJson" className="text-xs text-muted">
                    columns (JSON)
                  </label>
                  <textarea
                    id="schemaColumnsJson"
                    value={columnsJson}
                    onChange={(e) => setColumnsJson(e.target.value)}
                    className={cn(
                      'w-full min-h-56 px-3 py-2 rounded-lg resize-y',
                      'surface elevated border border-default',
                      'focus:outline-none focus:ring-2 focus:ring-primary',
                      'placeholder:text-muted text-xs font-code'
                    )}
                    spellCheck={false}
                  />
                </div>
                <div className="space-y-1">
                  <label htmlFor="schemaRelationshipsJson" className="text-xs text-muted">
                    relationships (JSON)
                  </label>
                  <textarea
                    id="schemaRelationshipsJson"
                    value={relationshipsJson}
                    onChange={(e) => setRelationshipsJson(e.target.value)}
                    className={cn(
                      'w-full min-h-56 px-3 py-2 rounded-lg resize-y',
                      'surface elevated border border-default',
                      'focus:outline-none focus:ring-2 focus:ring-primary',
                      'placeholder:text-muted text-xs font-code'
                    )}
                    spellCheck={false}
                  />
                </div>
              </div>

              <div className="text-xs text-muted">
                Tip: `columns` should follow `backend/data/schema.json` format (name/type/primary_key/description).
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
};

