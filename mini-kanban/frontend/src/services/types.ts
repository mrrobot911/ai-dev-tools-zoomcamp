import type {
  User,
  Board,
  Column,
  Card,
  Participant,
  Invitation,
  BoardWithDetails,
} from '@/types';

export interface CreateBoardInput {
  name: string;
}

export interface UpdateBoardInput {
  name: string;
}

export interface CreateColumnInput {
  boardId: string;
  name: string;
}

export interface UpdateColumnInput {
  name?: string;
  order?: number;
}

export interface CreateCardInput {
  boardId: string;
  columnId: string;
  title: string;
  description?: string;
  assigneeId?: string | null;
}

export interface UpdateCardInput {
  title?: string;
  description?: string;
  assigneeId?: string | null;
}

export interface MoveCardInput {
  cardId: string;
  targetColumnId: string;
}

export interface RegisterInput {
  email: string;
  password: string;
  name: string;
  invitationToken?: string;
}

export interface LoginInput {
  email: string;
  password: string;
}

export interface BoardSummary {
  board: Board;
  participantCount: number;
  role: 'owner' | 'participant';
}

export interface KanbanService {
  // Auth
  register(input: RegisterInput): Promise<{ user: User; token: string }>;
  login(input: LoginInput): Promise<{ user: User; token: string }>;
  logout(): Promise<void>;
  getCurrentUser(): Promise<User | null>;

  // Boards
  listBoards(): Promise<BoardSummary[]>;
  getBoard(boardId: string): Promise<BoardWithDetails>;
  createBoard(input: CreateBoardInput): Promise<Board>;
  updateBoard(boardId: string, input: UpdateBoardInput): Promise<Board>;
  deleteBoard(boardId: string): Promise<void>;

  // Columns
  createColumn(boardId: string, input: CreateColumnInput): Promise<Column>;
  updateColumn(boardId: string, columnId: string, input: UpdateColumnInput): Promise<Column>;
  deleteColumn(boardId: string, columnId: string): Promise<void>;
  reorderColumns(boardId: string, columnIds: string[]): Promise<Column[]>;

  // Cards
  createCard(boardId: string, input: CreateCardInput): Promise<Card>;
  updateCard(boardId: string, cardId: string, input: UpdateCardInput): Promise<Card>;
  deleteCard(boardId: string, cardId: string): Promise<void>;
  moveCard(boardId: string, input: MoveCardInput): Promise<Card>;

  // Participants
  removeParticipant(boardId: string, userId: string): Promise<void>;
  leaveBoard(boardId: string): Promise<void>;

  // Invitations
  createInvitation(boardId: string): Promise<Invitation>;
  listInvitations(boardId: string): Promise<Invitation[]>;
  getInvitationByToken(token: string): Promise<Invitation | null>;

  // Search
  searchCards(boardId: string, query: string): Promise<Card[]>;
  filterCardsByAssignee(boardId: string, assigneeId: string | null): Promise<Card[]>;
}
