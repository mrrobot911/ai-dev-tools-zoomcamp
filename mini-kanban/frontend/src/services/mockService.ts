import type {
  User,
  Board,
  Column,
  Card,
  Participant,
  Invitation,
  BoardWithDetails,
  Role,
} from '@/types';
import { LIMITS, DEFAULT_COLUMNS } from '@/types';
import type {
  KanbanService,
  RegisterInput,
  LoginInput,
  CreateBoardInput,
  UpdateBoardInput,
  CreateColumnInput,
  UpdateColumnInput,
  CreateCardInput,
  UpdateCardInput,
  MoveCardInput,
  BoardSummary,
} from '@/services/types';
import { db, uid, nowISO } from '@/services/mockData';

let currentUserId: string | null = null;

function delay(ms = 150): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function requireAuth(): User {
  if (!currentUserId) throw new Error('Not authenticated');
  const user = db.users.get(currentUserId);
  if (!user) throw new Error('User not found');
  return user;
}

function getBoardOrThrow(boardId: string): Board {
  const board = db.boards.get(boardId);
  if (!board) throw new Error('Board not found');
  return board;
}

function getBoardParticipants(boardId: string): Participant[] {
  return db.participants.get(boardId) ?? [];
}

function isParticipant(boardId: string, userId: string): boolean {
  const parts = getBoardParticipants(boardId);
  return parts.some((p) => p.userId === userId);
}

function getRole(boardId: string, userId: string): Role | null {
  const parts = getBoardParticipants(boardId);
  const p = parts.find((p) => p.userId === userId);
  return p ? p.role : null;
}

function requireBoardAccess(boardId: string): User {
  const user = requireAuth();
  if (!isParticipant(boardId, user.id)) {
    const err = new Error('Access denied');
    (err as Error & { status: number }).status = 403;
    throw err;
  }
  return user;
}

function requireOwner(boardId: string): User {
  const user = requireBoardAccess(boardId);
  if (getRole(boardId, user.id) !== 'owner') {
    const err = new Error('Only the owner can perform this action');
    (err as Error & { status: number }).status = 403;
    throw err;
  }
  return user;
}

function getBoardColumns(boardId: string): Column[] {
  return Array.from(db.columns.values())
    .filter((c) => c.boardId === boardId)
    .sort((a, b) => a.order - b.order);
}

function getBoardCards(boardId: string): Card[] {
  return Array.from(db.cards.values())
    .filter((c) => c.boardId === boardId)
    .sort((a, b) => a.createdAt.localeCompare(b.createdAt));
}

function buildBoardWithDetails(board: Board, userId: string): BoardWithDetails {
  const participants = getBoardParticipants(board.id);
  const role = participants.find((p) => p.userId === userId)?.role ?? 'participant';
  return {
    ...board,
    participants,
    columns: getBoardColumns(board.id),
    cards: getBoardCards(board.id),
    role,
  };
}

function addParticipant(boardId: string, user: User, role: Role): void {
  const parts = getBoardParticipants(boardId);
  if (parts.length >= LIMITS.MAX_PARTICIPANTS_PER_BOARD) {
    throw new Error('Board has reached the maximum number of participants');
  }
  parts.push({
    userId: user.id,
    email: user.email,
    name: user.name,
    role,
    joinedAt: nowISO(),
  });
  db.participants.set(boardId, parts);

  const userBoards = db.boardParticipants.get(user.id) ?? new Set();
  userBoards.add(boardId);
  db.boardParticipants.set(user.id, userBoards);
}

function removeParticipantInternal(boardId: string, userId: string): void {
  const parts = getBoardParticipants(boardId);
  const filtered = parts.filter((p) => p.userId !== userId);
  db.participants.set(boardId, filtered);

  const userBoards = db.boardParticipants.get(userId);
  if (userBoards) {
    userBoards.delete(boardId);
  }
}

function deleteBoardInternal(boardId: string): void {
  // Delete cards
  for (const [cardId, card] of db.cards) {
    if (card.boardId === boardId) db.cards.delete(cardId);
  }
  // Delete columns
  for (const [colId, col] of db.columns) {
    if (col.boardId === boardId) db.columns.delete(colId);
  }
  // Remove participants
  const parts = getBoardParticipants(boardId);
  for (const p of parts) {
    const userBoards = db.boardParticipants.get(p.userId);
    if (userBoards) userBoards.delete(boardId);
  }
  db.participants.delete(boardId);
  db.invitations.delete(boardId);
  db.boards.delete(boardId);
}

export const mockService: KanbanService = {
  // ── Auth ──────────────────────────────────────────────
  async register(input: RegisterInput): Promise<{ user: User; token: string }> {
    await delay();
    const email = input.email.trim().toLowerCase();
    if (!email) throw new Error('Email is required');
    if (!input.password || input.password.length < 4)
      throw new Error('Password must be at least 4 characters');
    if (!input.name.trim()) throw new Error('Name is required');

    const existing = Array.from(db.users.values()).find((u) => u.email === email);
    if (existing) throw new Error('A user with this email already exists');

    const user: User = {
      id: uid('user'),
      email,
      name: input.name.trim(),
      createdAt: nowISO(),
    };
    db.users.set(user.id, user);
    db.passwords.set(email, input.password);

    // Handle invitation
    if (input.invitationToken) {
      const allInvites = Array.from(db.invitations.values()).flat();
      const invite = allInvites.find((i) => i.token === input.invitationToken);
      if (!invite) throw new Error('Invalid invitation link');
      if (invite.used) throw new Error('This invitation link has already been used');
      const board = getBoardOrThrow(invite.boardId);
      addParticipant(board.id, user, 'participant');
      invite.used = true;
    }

    currentUserId = user.id;
    return { user, token: uid('token') };
  },

  async login(input: LoginInput): Promise<{ user: User; token: string }> {
    await delay();
    const email = input.email.trim().toLowerCase();
    const user = Array.from(db.users.values()).find((u) => u.email === email);
    if (!user) throw new Error('Invalid credentials');
    const storedPassword = db.passwords.get(email);
    if (storedPassword !== input.password) throw new Error('Invalid credentials');
    currentUserId = user.id;
    return { user, token: uid('token') };
  },

  async logout(): Promise<void> {
    await delay(50);
    currentUserId = null;
  },

  async getCurrentUser(): Promise<User | null> {
    if (!currentUserId) return null;
    return db.users.get(currentUserId) ?? null;
  },

  // ── Boards ─────────────────────────────────────────────
  async listBoards(): Promise<BoardSummary[]> {
    await delay();
    const user = requireAuth();
    const boardIds = db.boardParticipants.get(user.id) ?? new Set();
    const summaries: BoardSummary[] = [];
    for (const boardId of boardIds) {
      const board = db.boards.get(boardId);
      if (!board) continue;
      const parts = getBoardParticipants(boardId);
      const role = parts.find((p) => p.userId === user.id)?.role ?? 'participant';
      summaries.push({
        board,
        participantCount: parts.length,
        role,
      });
    }
    return summaries.sort((a, b) => b.board.createdAt.localeCompare(a.board.createdAt));
  },

  async getBoard(boardId: string): Promise<BoardWithDetails> {
    await delay();
    const user = requireBoardAccess(boardId);
    const board = getBoardOrThrow(boardId);
    return buildBoardWithDetails(board, user.id);
  },

  async createBoard(input: CreateBoardInput): Promise<Board> {
    await delay();
    const user = requireAuth();
    const boardCount = db.boardParticipants.get(user.id)?.size ?? 0;
    if (boardCount >= LIMITS.MAX_BOARDS_PER_USER)
      throw new Error('You have reached the maximum number of boards (10)');

    if (!input.name.trim()) throw new Error('Board name is required');

    const board: Board = {
      id: uid('board'),
      name: input.name.trim(),
      ownerId: user.id,
      ownerName: user.name,
      createdAt: nowISO(),
      updatedAt: nowISO(),
    };
    db.boards.set(board.id, board);
    db.participants.set(board.id, []);
    db.invitations.set(board.id, []);
    addParticipant(board.id, user, 'owner');

    // Create default columns
    DEFAULT_COLUMNS.forEach((name, i) => {
      const col: Column = {
        id: uid('col'),
        boardId: board.id,
        name,
        order: i,
        createdAt: nowISO(),
      };
      db.columns.set(col.id, col);
    });

    return board;
  },

  async updateBoard(boardId: string, input: UpdateBoardInput): Promise<Board> {
    await delay();
    requireOwner(boardId);
    const board = getBoardOrThrow(boardId);
    if (!input.name.trim()) throw new Error('Board name is required');
    board.name = input.name.trim();
    board.updatedAt = nowISO();
    db.boards.set(boardId, board);
    return board;
  },

  async deleteBoard(boardId: string): Promise<void> {
    await delay();
    requireOwner(boardId);
    deleteBoardInternal(boardId);
  },

  // ── Columns ────────────────────────────────────────────
  async createColumn(boardId: string, input: CreateColumnInput): Promise<Column> {
    await delay();
    requireOwner(boardId);
    const cols = getBoardColumns(boardId);
    if (cols.length >= LIMITS.MAX_COLUMNS_PER_BOARD)
      throw new Error('Board has reached the maximum number of columns (10)');
    if (!input.name.trim()) throw new Error('Column name is required');
    const col: Column = {
      id: uid('col'),
      boardId,
      name: input.name.trim(),
      order: cols.length,
      createdAt: nowISO(),
    };
    db.columns.set(col.id, col);
    return col;
  },

  async updateColumn(
    boardId: string,
    columnId: string,
    input: UpdateColumnInput
  ): Promise<Column> {
    await delay();
    requireOwner(boardId);
    const col = db.columns.get(columnId);
    if (!col || col.boardId !== boardId) throw new Error('Column not found');
    if (input.name !== undefined) {
      if (!input.name.trim()) throw new Error('Column name is required');
      col.name = input.name.trim();
    }
    if (input.order !== undefined) col.order = input.order;
    db.columns.set(columnId, col);
    return col;
  },

  async deleteColumn(boardId: string, columnId: string): Promise<void> {
    await delay();
    requireOwner(boardId);
    const cols = getBoardColumns(boardId);
    if (cols.length <= LIMITS.MIN_COLUMNS_PER_BOARD)
      throw new Error('A board must have at least 3 columns');
    const col = db.columns.get(columnId);
    if (!col || col.boardId !== boardId) throw new Error('Column not found');
    const cardsInCol = getBoardCards(boardId).filter((c) => c.columnId === columnId);
    if (cardsInCol.length > 0)
      throw new Error('Cannot delete a column that contains cards');
    db.columns.delete(columnId);
    // Reorder remaining columns
    const remaining = getBoardColumns(boardId);
    remaining.forEach((c, i) => {
      c.order = i;
      db.columns.set(c.id, c);
    });
  },

  async reorderColumns(boardId: string, columnIds: string[]): Promise<Column[]> {
    await delay();
    requireOwner(boardId);
    columnIds.forEach((cid, i) => {
      const col = db.columns.get(cid);
      if (col && col.boardId === boardId) {
        col.order = i;
        db.columns.set(cid, col);
      }
    });
    return getBoardColumns(boardId);
  },

  // ── Cards ─────────────────────────────────────────────
  async createCard(boardId: string, input: CreateCardInput): Promise<Card> {
    await delay();
    const user = requireBoardAccess(boardId);
    const col = db.columns.get(input.columnId);
    if (!col || col.boardId !== boardId) throw new Error('Column not found');
    const cardsInCol = getBoardCards(boardId).filter((c) => c.columnId === input.columnId);
    if (cardsInCol.length >= LIMITS.MAX_CARDS_PER_COLUMN)
      throw new Error('Column has reached the maximum number of cards (100)');
    if (!input.title.trim()) throw new Error('Card title is required');

    let assigneeName: string | null = null;
    if (input.assigneeId) {
      const parts = getBoardParticipants(boardId);
      const assignee = parts.find((p) => p.userId === input.assigneeId);
      if (!assignee) throw new Error('Assignee must be a board participant');
      assigneeName = assignee.name;
    }

    const card: Card = {
      id: uid('card'),
      boardId,
      columnId: input.columnId,
      title: input.title.trim(),
      description: input.description?.trim() ?? '',
      creatorId: user.id,
      creatorName: user.name,
      assigneeId: input.assigneeId ?? null,
      assigneeName,
      createdAt: nowISO(),
      updatedAt: nowISO(),
    };
    db.cards.set(card.id, card);
    return card;
  },

  async updateCard(boardId: string, cardId: string, input: UpdateCardInput): Promise<Card> {
    await delay();
    requireBoardAccess(boardId);
    const card = db.cards.get(cardId);
    if (!card || card.boardId !== boardId) throw new Error('Card not found');
    if (input.title !== undefined) {
      if (!input.title.trim()) throw new Error('Card title is required');
      card.title = input.title.trim();
    }
    if (input.description !== undefined) {
      card.description = input.description.trim();
    }
    if (input.assigneeId !== undefined) {
      if (input.assigneeId) {
        const parts = getBoardParticipants(boardId);
        const assignee = parts.find((p) => p.userId === input.assigneeId);
        if (!assignee) throw new Error('Assignee must be a board participant');
        card.assigneeId = input.assigneeId;
        card.assigneeName = assignee.name;
      } else {
        card.assigneeId = null;
        card.assigneeName = null;
      }
    }
    card.updatedAt = nowISO();
    db.cards.set(cardId, card);
    return card;
  },

  async deleteCard(boardId: string, cardId: string): Promise<void> {
    await delay();
    const user = requireBoardAccess(boardId);
    const card = db.cards.get(cardId);
    if (!card || card.boardId !== boardId) throw new Error('Card not found');
    const role = getRole(boardId, user.id);
    if (role !== 'owner' && card.creatorId !== user.id)
      throw new Error('Only the card creator or board owner can delete this card');
    db.cards.delete(cardId);
  },

  async moveCard(boardId: string, input: MoveCardInput): Promise<Card> {
    await delay(100);
    requireBoardAccess(boardId);
    const card = db.cards.get(input.cardId);
    if (!card || card.boardId !== boardId) throw new Error('Card not found');
    const targetCol = db.columns.get(input.targetColumnId);
    if (!targetCol || targetCol.boardId !== boardId)
      throw new Error('Target column not found');
    const cardsInTarget = getBoardCards(boardId).filter(
      (c) => c.columnId === input.targetColumnId && c.id !== input.cardId
    );
    if (cardsInTarget.length >= LIMITS.MAX_CARDS_PER_COLUMN)
      throw new Error('Target column has reached the maximum number of cards (100)');
    card.columnId = input.targetColumnId;
    card.updatedAt = nowISO();
    db.cards.set(input.cardId, card);
    return card;
  },

  // ── Participants ──────────────────────────────────────
  async removeParticipant(boardId: string, userId: string): Promise<void> {
    await delay();
    requireOwner(boardId);
    const parts = getBoardParticipants(boardId);
    const target = parts.find((p) => p.userId === userId);
    if (!target) throw new Error('Participant not found');
    if (target.role === 'owner') throw new Error('Cannot remove the board owner');
    removeParticipantInternal(boardId, userId);
  },

  async leaveBoard(boardId: string): Promise<void> {
    await delay();
    const user = requireBoardAccess(boardId);
    const parts = getBoardParticipants(boardId);
    if (parts.length <= 1) throw new Error('Cannot leave a board with no other participants');
    const isOwner = parts.find((p) => p.userId === user.id)?.role === 'owner';
    if (isOwner) throw new Error('The owner cannot leave the board. Delete it instead.');
    removeParticipantInternal(boardId, user.id);
  },

  // ── Invitations ───────────────────────────────────────
  async createInvitation(boardId: string): Promise<Invitation> {
    await delay();
    requireOwner(boardId);
    const board = getBoardOrThrow(boardId);
    const parts = getBoardParticipants(boardId);
    if (parts.length >= LIMITS.MAX_PARTICIPANTS_PER_BOARD)
      throw new Error('Board has reached the maximum number of participants');
    const invitation: Invitation = {
      id: uid('inv'),
      boardId,
      boardName: board.name,
      token: uid('inv_token'),
      used: false,
      createdAt: nowISO(),
      createdBy: currentUserId!,
    };
    const invites = db.invitations.get(boardId) ?? [];
    invites.push(invitation);
    db.invitations.set(boardId, invites);
    return invitation;
  },

  async listInvitations(boardId: string): Promise<Invitation[]> {
    await delay();
    requireOwner(boardId);
    return (db.invitations.get(boardId) ?? []).slice().reverse();
  },

  async getInvitationByToken(token: string): Promise<Invitation | null> {
    await delay(100);
    const allInvites = Array.from(db.invitations.values()).flat();
    return allInvites.find((i) => i.token === token) ?? null;
  },

  // ── Search ────────────────────────────────────────────
  async searchCards(boardId: string, query: string): Promise<Card[]> {
    await delay(100);
    requireBoardAccess(boardId);
    const cards = getBoardCards(boardId);
    const q = query.trim().toLowerCase();
    if (!q) return cards;
    return cards.filter((c) => c.title.toLowerCase().includes(q));
  },

  async filterCardsByAssignee(boardId: string, assigneeId: string | null): Promise<Card[]> {
    await delay(100);
    requireBoardAccess(boardId);
    const cards = getBoardCards(boardId);
    if (assigneeId === null) return cards;
    return cards.filter((c) => c.assigneeId === assigneeId);
  },
};

// Expose for tests
export function _resetMockData(): void {
  // This is a no-op in production; tests can import the db directly
}

export function _setCurrentUserId(id: string | null): void {
  currentUserId = id;
}

export function _getCurrentUserId(): string | null {
  return currentUserId;
}
