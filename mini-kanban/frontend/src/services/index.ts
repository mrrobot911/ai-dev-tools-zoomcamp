import { mockService } from '@/services/mockService';
import type { KanbanService } from '@/services/types';

// Centralized service layer — swap mockService for a real implementation later.
export const service: KanbanService = mockService;

export type { KanbanService } from '@/services/types';
