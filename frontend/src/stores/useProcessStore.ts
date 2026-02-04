import { create } from 'zustand';
import type {
  SSEEvent,
  StageInfo,
  SchemaEvent,
  SimilarExamplesEvent,
  ValidationEvent,
  ResultEvent,
  ErrorEvent,
} from '../types/events';

interface ProcessStore {
  conversationId: string | null;
  currentStage: string | null;
  stages: StageInfo[];
  intent: string | null;
  schema: SchemaEvent | null;
  similarExamples: SimilarExamplesEvent | null;
  generatedSQL: string | null;
  validation: ValidationEvent | null;
  results: ResultEvent | null;
  error: ErrorEvent | null;
  isComplete: boolean;
  
  updateFromSSE: (event: SSEEvent) => void;
  resetProcess: () => void;
  setStageStatus: (stage: string, status: StageInfo['status']) => void;
}

export const useProcessStore = create<ProcessStore>((set) => ({
  conversationId: null,
  currentStage: null,
  stages: [],
  intent: null,
  schema: null,
  similarExamples: null,
  generatedSQL: null,
  validation: null,
  results: null,
  error: null,
  isComplete: false,
  
  updateFromSSE: (event) => set((state) => {
    const updates: Partial<ProcessStore> = {};
    
    switch (event.type) {
      case 'conversation_id':
        updates.conversationId = event.data.conversation_id;
        break;
        
      case 'stage': {
        const { stage, message, icon } = event.data;
        updates.currentStage = stage;
        
        // Update or add stage in timeline
        const existingStageIndex = state.stages.findIndex(s => s.stage === stage);
        const newStages = [...state.stages];
        
        if (existingStageIndex >= 0) {
          newStages[existingStageIndex] = {
            ...newStages[existingStageIndex],
            status: 'active',
            message,
            icon,
          };
        } else {
          newStages.push({
            stage,
            message,
            icon,
            status: 'active',
            timestamp: Date.now(),
          });
        }
        
        // Mark previous stages as completed
        newStages.forEach((s, idx) => {
          if (s.stage !== stage && s.status === 'active') {
            newStages[idx].status = 'completed';
          }
        });
        
        updates.stages = newStages;
        break;
      }
      
      case 'intent':
        updates.intent = event.data.intent;
        break;
        
      case 'schema':
        updates.schema = event.data;
        break;
        
      case 'similar_examples':
        updates.similarExamples = event.data;
        break;
        
      case 'sql':
        updates.generatedSQL = event.data.sql;
        break;
        
      case 'validation':
        updates.validation = event.data;
        if (!event.data.valid) {
          // Mark validation stage as error
          const newStages = [...state.stages];
          const validationIdx = newStages.findIndex(s => s.stage === 'validating_sql');
          if (validationIdx >= 0) {
            newStages[validationIdx].status = 'error';
          }
          updates.stages = newStages;
        }
        break;
        
      case 'result':
        updates.results = event.data;
        break;
        
      case 'error':
        updates.error = event.data;
        // Mark current stage as error
        const newStages = [...state.stages];
        if (state.currentStage) {
          const idx = newStages.findIndex(s => s.stage === state.currentStage);
          if (idx >= 0) {
            newStages[idx].status = 'error';
          }
        }
        updates.stages = newStages;
        break;
        
      case 'complete':
        updates.isComplete = true;
        // Mark all stages as completed
        const completedStages = state.stages.map(s => ({
          ...s,
          status: s.status === 'error' ? 'error' : 'completed' as StageInfo['status'],
        }));
        updates.stages = completedStages;
        break;
    }
    
    return { ...updates };
  }),
  
  resetProcess: () => set({
    conversationId: null,
    currentStage: null,
    stages: [],
    intent: null,
    schema: null,
    similarExamples: null,
    generatedSQL: null,
    validation: null,
    results: null,
    error: null,
    isComplete: false,
  }),
  
  setStageStatus: (stage, status) => set((state) => {
    const newStages = [...state.stages];
    const idx = newStages.findIndex(s => s.stage === stage);
    if (idx >= 0) {
      newStages[idx].status = status;
    }
    return { stages: newStages };
  }),
}));
