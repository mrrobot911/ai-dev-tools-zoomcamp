import { describe, it, expect, beforeEach } from 'vitest';
import { mockService } from '@/services/mockService';
import { _setCurrentUserId } from '@/services/mockService';
import { db } from '@/services/mockData';
import { LIMITS } from '@/types';

// Helper: register a fresh user and return their info
async function registerUser(email: string, name: string, password = 'pass1234', invitationToken?: string) {
  return mockService.register({ email, password, name, invitationToken });
}

async function loginUser(email: string, password = 'pass1234') {
  return mockService.login({ email, password });
}

describe('Mock Service — Auth', () => {
  beforeEach(() => {
    _setCurrentUserId(null);
  });

  it('registers a new user', async () => {
    const { user } = await registerUser('test1@example.com', 'Test One');
    expect(user.email).toBe('test1@example.com');
    expect(user.name).toBe('Test One');
    expect(user.id).toBeTruthy();
  });

  it('rejects duplicate email registration', async () => {
    await registerUser('dup@example.com', 'Dup One');
    await expect(registerUser('dup@example.com', 'Dup Two')).rejects.toThrow(
      'already exists'
    );
  });

  it('logs in with valid credentials', async () => {
    await registerUser('login@example.com', 'Login User');
    const { user } = await loginUser('login@example.com');
    expect(user.email).toBe('login@example.com');
  });

  it('rejects invalid credentials', async () => {
    await registerUser('invalid@example.com', 'Invalid User');
    await expect(loginUser('invalid@example.com', 'wrongpass')).rejects.toThrow(
      'Invalid credentials'
    );
    await expect(loginUser('nonexistent@example.com')).rejects.toThrow(
      'Invalid credentials'
    );
  });

  it('logs out', async () => {
    await registerUser('logout@example.com', 'Logout User');
    await mockService.logout();
    const user = await mockService.getCurrentUser();
    expect(user).toBeNull();
  });

  it('rejects short passwords', async () => {
    await expect(
      registerUser('shortpw@example.com', 'Short', 'ab')
    ).rejects.toThrow('Password');
  });
});

describe('Mock Service — Boards', () => {
  let ownerId: string;

  beforeEach(async () => {
    _setCurrentUserId(null);
    const { user } = await registerUser('boardowner@example.com', 'Board Owner');
    ownerId = user.id;
  });

  it('creates a board with three default columns', async () => {
    const board = await mockService.createBoard({ name: 'Test Board' });
    expect(board.name).toBe('Test Board');
    expect(board.ownerId).toBe(ownerId);

    const details = await mockService.getBoard(board.id);
    expect(details.columns).toHaveLength(3);
    expect(details.columns.map((c) => c.name)).toEqual([
      'To Do',
      'In Progress',
      'Done',
    ]);
  });

  it('lists user boards with participant count', async () => {
    await mockService.createBoard({ name: 'Board A' });
    await mockService.createBoard({ name: 'Board B' });
    const boards = await mockService.listBoards();
    expect(boards).toHaveLength(2);
    expect(boards[0].participantCount).toBe(1);
    expect(boards[0].role).toBe('owner');
  });

  it('prevents creating more than 10 boards', async () => {
    for (let i = 0; i < LIMITS.MAX_BOARDS_PER_USER; i++) {
      await mockService.createBoard({ name: `Board ${i}` });
    }
    await expect(mockService.createBoard({ name: 'Extra' })).rejects.toThrow(
      'maximum'
    );
  });

  it('renames a board', async () => {
    const board = await mockService.createBoard({ name: 'Old Name' });
    const updated = await mockService.updateBoard(board.id, { name: 'New Name' });
    expect(updated.name).toBe('New Name');
  });

  it('prevents non-owner from renaming board', async () => {
    const board = await mockService.createBoard({ name: 'Owner Board' });
    // Create a second user and add them as participant
    const invite = await mockService.createInvitation(board.id);
    _setCurrentUserId(null);
    const { user: user2 } = await registerUser('participant@example.com', 'Participant', 'pass1234', invite.token);
    await expect(mockService.updateBoard(board.id, { name: 'Hacked' })).rejects.toThrow(
      'owner'
    );
  });

  it('deletes a board and all related data', async () => {
    const board = await mockService.createBoard({ name: 'To Delete' });
    await mockService.createCard(board.id, {
      boardId: board.id,
      columnId: (await mockService.getBoard(board.id)).columns[0].id,
      title: 'Test card',
    });
    await mockService.deleteBoard(board.id);
    await expect(mockService.getBoard(board.id)).rejects.toThrow('not found');
    expect(db.boards.has(board.id)).toBe(false);
    expect(db.columns.size).toBeLessThanOrEqual(3); // only demo board columns remain
  });

  it('rejects empty board name', async () => {
    await expect(mockService.createBoard({ name: '' })).rejects.toThrow('required');
  });
});

describe('Mock Service — Columns', () => {
  let boardId: string;
  let firstColumnId: string;

  beforeEach(async () => {
    _setCurrentUserId(null);
    await registerUser('colowner@example.com', 'Col Owner');
    const board = await mockService.createBoard({ name: 'Column Test Board' });
    boardId = board.id;
    const details = await mockService.getBoard(boardId);
    firstColumnId = details.columns[0].id;
  });

  it('creates a new column', async () => {
    const col = await mockService.createColumn(boardId, { boardId, name: 'New Col' });
    expect(col.name).toBe('New Col');
    const details = await mockService.getBoard(boardId);
    expect(details.columns).toHaveLength(4);
  });

  it('prevents creating more than 10 columns', async () => {
    for (let i = 0; i < 7; i++) {
      await mockService.createColumn(boardId, { boardId, name: `Col ${i}` });
    }
    const details = await mockService.getBoard(boardId);
    expect(details.columns).toHaveLength(10);
    await expect(
      mockService.createColumn(boardId, { boardId, name: 'Extra' })
    ).rejects.toThrow('maximum');
  });

  it('renames a column', async () => {
    const updated = await mockService.updateColumn(boardId, firstColumnId, {
      name: 'Renamed',
    });
    expect(updated.name).toBe('Renamed');
  });

  it('prevents deleting a column with cards', async () => {
    await mockService.createCard(boardId, {
      boardId,
      columnId: firstColumnId,
      title: 'Card in column',
    });
    await expect(
      mockService.deleteColumn(boardId, firstColumnId)
    ).rejects.toThrow('contains cards');
  });

  it('prevents deleting when only 3 columns remain', async () => {
    await expect(
      mockService.deleteColumn(boardId, firstColumnId)
    ).rejects.toThrow('at least 3');
  });

  it('reorders columns', async () => {
    const details = await mockService.getBoard(boardId);
    const colIds = details.columns.map((c) => c.id);
    const reversed = [...colIds].reverse();
    await mockService.reorderColumns(boardId, reversed);
    const updated = await mockService.getBoard(boardId);
    expect(updated.columns.map((c) => c.id)).toEqual(reversed);
  });

  it('prevents non-owner from creating columns', async () => {
    const invite = await mockService.createInvitation(boardId);
    _setCurrentUserId(null);
    await registerUser('colpart@example.com', 'Col Part', 'pass1234', invite.token);
    await expect(
      mockService.createColumn(boardId, { boardId, name: 'Nope' })
    ).rejects.toThrow('owner');
  });
});

describe('Mock Service — Cards', () => {
  let boardId: string;
  let columnId: string;

  beforeEach(async () => {
    _setCurrentUserId(null);
    await registerUser('cardowner@example.com', 'Card Owner');
    const board = await mockService.createBoard({ name: 'Card Test Board' });
    boardId = board.id;
    const details = await mockService.getBoard(boardId);
    columnId = details.columns[0].id;
  });

  it('creates a card with title', async () => {
    const card = await mockService.createCard(boardId, {
      boardId,
      columnId,
      title: 'My Task',
    });
    expect(card.title).toBe('My Task');
    expect(card.columnId).toBe(columnId);
    expect(card.creatorName).toBe('Card Owner');
  });

  it('rejects card without title', async () => {
    await expect(
      mockService.createCard(boardId, { boardId, columnId, title: '' })
    ).rejects.toThrow('required');
  });

  it('updates a card', async () => {
    const card = await mockService.createCard(boardId, {
      boardId,
      columnId,
      title: 'Original',
    });
    const updated = await mockService.updateCard(boardId, card.id, {
      title: 'Updated',
      description: 'New desc',
    });
    expect(updated.title).toBe('Updated');
    expect(updated.description).toBe('New desc');
  });

  it('allows any participant to edit cards', async () => {
    const card = await mockService.createCard(boardId, {
      boardId,
      columnId,
      title: 'Edit Me',
    });
    const invite = await mockService.createInvitation(boardId);
    _setCurrentUserId(null);
    await registerUser('editor@example.com', 'Editor', 'pass1234', invite.token);
    const updated = await mockService.updateCard(boardId, card.id, {
      title: 'Edited by participant',
    });
    expect(updated.title).toBe('Edited by participant');
  });

  it('allows card creator to delete their card', async () => {
    const card = await mockService.createCard(boardId, {
      boardId,
      columnId,
      title: 'Delete Me',
    });
    await mockService.deleteCard(boardId, card.id);
    const details = await mockService.getBoard(boardId);
    expect(details.cards.find((c) => c.id === card.id)).toBeUndefined();
  });

  it('allows owner to delete any card', async () => {
    const card = await mockService.createCard(boardId, {
      boardId,
      columnId,
      title: 'Owner Delete',
    });
    const invite = await mockService.createInvitation(boardId);
    _setCurrentUserId(null);
    await registerUser('other@example.com', 'Other', 'pass1234', invite.token);
    // Non-creator, non-owner cannot delete
    await expect(mockService.deleteCard(boardId, card.id)).rejects.toThrow(
      'creator or board owner'
    );
    // Switch back to owner
    const { user: owner } = await loginUser('cardowner@example.com');
    _setCurrentUserId(owner.id);
    await mockService.deleteCard(boardId, card.id);
    const details = await mockService.getBoard(boardId);
    expect(details.cards.find((c) => c.id === card.id)).toBeUndefined();
  });

  it('moves a card between columns', async () => {
    const details = await mockService.getBoard(boardId);
    const targetCol = details.columns[1].id;
    const card = await mockService.createCard(boardId, {
      boardId,
      columnId,
      title: 'Move Me',
    });
    const moved = await mockService.moveCard(boardId, {
      cardId: card.id,
      targetColumnId: targetCol,
    });
    expect(moved.columnId).toBe(targetCol);
  });

  it('assigns a card to a participant', async () => {
    const details = await mockService.getBoard(boardId);
    const ownerId = details.participants[0].userId;
    const card = await mockService.createCard(boardId, {
      boardId,
      columnId,
      title: 'Assigned',
      assigneeId: ownerId,
    });
    expect(card.assigneeId).toBe(ownerId);
    expect(card.assigneeName).toBe('Card Owner');
  });

  it('rejects assignee who is not a participant', async () => {
    await expect(
      mockService.createCard(boardId, {
        boardId,
        columnId,
        title: 'Bad Assignee',
        assigneeId: 'fake-user-id',
      })
    ).rejects.toThrow('participant');
  });
});

describe('Mock Service — Search & Filter', () => {
  let boardId: string;
  let columnId: string;

  beforeEach(async () => {
    _setCurrentUserId(null);
    await registerUser('searchowner@example.com', 'Search Owner');
    const board = await mockService.createBoard({ name: 'Search Board' });
    boardId = board.id;
    const details = await mockService.getBoard(boardId);
    columnId = details.columns[0].id;
    await mockService.createCard(boardId, { boardId, columnId, title: 'Buy groceries' });
    await mockService.createCard(boardId, { boardId, columnId, title: 'Clean kitchen' });
    await mockService.createCard(boardId, { boardId, columnId, title: 'Walk the dog' });
  });

  it('searches cards by title', async () => {
    const results = await mockService.searchCards(boardId, 'kitchen');
    expect(results).toHaveLength(1);
    expect(results[0].title).toBe('Clean kitchen');
  });

  it('search is case-insensitive', async () => {
    const results = await mockService.searchCards(boardId, 'BUY');
    expect(results).toHaveLength(1);
    expect(results[0].title).toBe('Buy groceries');
  });

  it('returns all cards for empty search', async () => {
    const results = await mockService.searchCards(boardId, '');
    expect(results).toHaveLength(3);
  });

  it('filters by assignee', async () => {
    const details = await mockService.getBoard(boardId);
    const ownerId = details.participants[0].userId;
    await mockService.updateCard(boardId, details.cards[0].id, {
      assigneeId: ownerId,
    });
    const filtered = await mockService.filterCardsByAssignee(boardId, ownerId);
    expect(filtered).toHaveLength(1);
    expect(filtered[0].title).toBe('Buy groceries');
  });

  it('filters by unassigned (null)', async () => {
    const all = await mockService.filterCardsByAssignee(boardId, null);
    expect(all).toHaveLength(3);
  });
});

describe('Mock Service — Invitations', () => {
  let boardId: string;

  beforeEach(async () => {
    _setCurrentUserId(null);
    await registerUser('invowner@example.com', 'Inv Owner');
    const board = await mockService.createBoard({ name: 'Invite Board' });
    boardId = board.id;
  });

  it('creates a single-use invitation', async () => {
    const inv = await mockService.createInvitation(boardId);
    expect(inv.token).toBeTruthy();
    expect(inv.used).toBe(false);
    expect(inv.boardId).toBe(boardId);
  });

  it('invitation becomes invalid after use', async () => {
    const inv = await mockService.createInvitation(boardId);
    _setCurrentUserId(null);
    await registerUser('invited@example.com', 'Invited', 'pass1234', inv.token);
    const usedInv = await mockService.getInvitationByToken(inv.token);
    expect(usedInv?.used).toBe(true);
    // Second use should fail
    _setCurrentUserId(null);
    await expect(
      registerUser('invited2@example.com', 'Invited2', 'pass1234', inv.token)
    ).rejects.toThrow('already been used');
  });

  it('auto-joins board after registering via invitation', async () => {
    const inv = await mockService.createInvitation(boardId);
    _setCurrentUserId(null);
    const { user } = await registerUser('joined@example.com', 'Joined', 'pass1234', inv.token);
    const details = await mockService.getBoard(boardId);
    expect(details.participants.find((p) => p.userId === user.id)).toBeDefined();
    expect(details.participants.find((p) => p.userId === user.id)?.role).toBe(
      'participant'
    );
  });

  it('prevents non-owner from creating invitations', async () => {
    const invite = await mockService.createInvitation(boardId);
    _setCurrentUserId(null);
    await registerUser('nope@example.com', 'Nope', 'pass1234', invite.token);
    await expect(mockService.createInvitation(boardId)).rejects.toThrow('owner');
  });

  it('rejects invalid invitation token', async () => {
    _setCurrentUserId(null);
    await expect(
      registerUser('bad@example.com', 'Bad', 'pass1234', 'invalid-token')
    ).rejects.toThrow('Invalid invitation');
  });

  it('prevents exceeding max participants via invitation', async () => {
    // Fill to 10 participants
    for (let i = 0; i < 9; i++) {
      const inv = await mockService.createInvitation(boardId);
      _setCurrentUserId(null);
      await registerUser(`filler${i}@example.com`, `Filler ${i}`, 'pass1234', inv.token);
      // Switch back to owner for next invitation
      const { user: owner } = await loginUser('invowner@example.com');
      _setCurrentUserId(owner.id);
    }
    const details = await mockService.getBoard(boardId);
    expect(details.participants).toHaveLength(10);
    await expect(mockService.createInvitation(boardId)).rejects.toThrow('maximum');
  });
});

describe('Mock Service — Participants', () => {
  let boardId: string;

  beforeEach(async () => {
    _setCurrentUserId(null);
    await registerUser('partowner@example.com', 'Part Owner');
    const board = await mockService.createBoard({ name: 'Part Board' });
    boardId = board.id;
  });

  it('owner can remove a participant', async () => {
    const inv = await mockService.createInvitation(boardId);
    _setCurrentUserId(null);
    const { user: p } = await registerUser('remove@example.com', 'Remove Me', 'pass1234', inv.token);
    // Switch to owner
    const { user: owner } = await loginUser('partowner@example.com');
    _setCurrentUserId(owner.id);
    await mockService.removeParticipant(boardId, p.id);
    const details = await mockService.getBoard(boardId);
    expect(details.participants.find((pp) => pp.userId === p.id)).toBeUndefined();
  });

  it('participant can leave the board', async () => {
    const inv = await mockService.createInvitation(boardId);
    _setCurrentUserId(null);
    await registerUser('leaver@example.com', 'Leaver', 'pass1234', inv.token);
    await mockService.leaveBoard(boardId);
    await expect(mockService.getBoard(boardId)).rejects.toThrow('Access denied');
  });

  it('owner cannot leave their own board', async () => {
    await expect(mockService.leaveBoard(boardId)).rejects.toThrow('owner');
  });

  it('cannot remove the board owner', async () => {
    const details = await mockService.getBoard(boardId);
    const ownerId = details.participants[0].userId;
    await expect(mockService.removeParticipant(boardId, ownerId)).rejects.toThrow(
      'Cannot remove the board owner'
    );
  });

  it('prevents non-owner from removing participants', async () => {
    const inv = await mockService.createInvitation(boardId);
    _setCurrentUserId(null);
    await registerUser('nonowner@example.com', 'Non Owner', 'pass1234', inv.token);
    const details = await mockService.getBoard(boardId);
    const ownerId = details.participants[0].userId;
    await expect(mockService.removeParticipant(boardId, ownerId)).rejects.toThrow(
      'owner'
    );
  });

  it('cannot access board without being a participant', async () => {
    _setCurrentUserId(null);
    await registerUser('outsider@example.com', 'Outsider');
    await expect(mockService.getBoard(boardId)).rejects.toThrow('Access denied');
  });
});

describe('Mock Service — Limits', () => {
  it('enforces max 100 cards per column', async () => {
    _setCurrentUserId(null);
    await registerUser('limitowner@example.com', 'Limit Owner');
    const board = await mockService.createBoard({ name: 'Limit Board' });
    const details = await mockService.getBoard(board.id);
    const colId = details.columns[0].id;
    for (let i = 0; i < LIMITS.MAX_CARDS_PER_COLUMN; i++) {
      await mockService.createCard(board.id, {
        boardId: board.id,
        columnId: colId,
        title: `Card ${i}`,
      });
    }
    await expect(
      mockService.createCard(board.id, {
        boardId: board.id,
        columnId: colId,
        title: 'Extra card',
      })
    ).rejects.toThrow('maximum');
  });
});
