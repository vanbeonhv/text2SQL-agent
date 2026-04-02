import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api } from '../services/api';
import type { SchemaTableDefinition } from '../types/api';

export const useSchemaTables = (activeOnly: boolean = true) => {
  return useQuery<SchemaTableDefinition[]>({
    queryKey: ['schemaTables', { activeOnly }],
    queryFn: () => api.listSchemaTables(activeOnly),
    staleTime: 30_000,
  });
};

export const useUpsertSchemaTable = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: SchemaTableDefinition) => api.upsertSchemaTable(payload),
    onSuccess: async () => {
      await qc.invalidateQueries({ queryKey: ['schemaTables'] });
    },
  });
};

export const useUpdateSchemaTable = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ tableName, payload }: { tableName: string; payload: SchemaTableDefinition }) =>
      api.updateSchemaTable(tableName, payload),
    onSuccess: async (_, vars) => {
      await Promise.all([
        qc.invalidateQueries({ queryKey: ['schemaTables'] }),
        qc.invalidateQueries({ queryKey: ['schemaTable', { tableName: vars.tableName }] }),
      ]);
    },
  });
};

export const useDeleteSchemaTable = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (tableName: string) => api.deleteSchemaTable(tableName),
    onSuccess: async () => {
      await qc.invalidateQueries({ queryKey: ['schemaTables'] });
    },
  });
};

