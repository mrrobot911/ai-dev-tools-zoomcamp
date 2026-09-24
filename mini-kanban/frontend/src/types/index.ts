export interface User {
  id: string;
  email: string;
  name: string;
  createdAt: string;
}

export interface Board {
  id: string;
  name: string;
  ownerId: string;
  ownerName: string;
  createdAt: string;
  updatedAt: string;
}

export interface Participant {
  userId: string;
  email: string;
  name: string;
  role: 'owner' | 'participant';
  joinedAt: string;
}

export interface Column {
  id: string;
  boardId: string;
  name: string;
  order: number;
  createdAt: string;
}

export interface Card {
  id: string;
  boardId: string;
  columnId: string;
  title: string;
  description: string;
  creatorId: string;
  creatorName: string;
  assigneeId: string | null;
  assigneeName: string | null;
  createdAt: string;
  updatedAt: string;
}

export interface Invitation {
  id: string;
  boardId: string;
  boardName: string;
  token: string;
  used: boolean;
  createdAt: string;
  createdBy: string;
}

export type Role = 'owner' | 'participant';

export interface AuthSession {
  user: User;
  token: string;
}

export interface BoardWithDetails extends Board {
  participants: Participant[];
  columns: Column[];
  cards: Card[];
  role: Role;
}

export const LIMITS = {
  MAX_BOARDS_PER_USER: 10,
  MAX_PARTICIPANTS_PER_BOARD: 10,
  MAX_COLUMNS_PER_BOARD: 10,
  MIN_COLUMNS_PER_BOARD: 3,
  MAX_CARDS_PER_COLUMN: 100,
} as const;

export const DEFAULT_COLUMNS = ['To Do', 'In Progress', 'Done'] as const;

export interface BoardEvent {
  entity_type: 'board' | 'column' | 'card' | 'participant';
  action: 'created' | 'updated' | 'deleted';
  entity_id: string;
  timestamp: string;
  payload: any | null;
}