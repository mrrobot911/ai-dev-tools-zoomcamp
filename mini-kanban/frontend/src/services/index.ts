import { apiService } from '@/services/apiService';
import type { KanbanService } from '@/services/types';

// Real backend client — connects to the FastAPI backend
export const service: KanbanService = apiService;

export type { KanbanService } from '@/services/types';
