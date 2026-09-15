import type {
  User,
  Board,
  Column,
  Card,
  Participant,
  Invitation,
} from '@/types';
import { DEFAULT_COLUMNS } from '@/types';

interface MockDatabase {
  users: Map<string, User>;
  passwords: Map<string, string>; // email -> password
  boards: Map<string, Board>;
  columns: Map<string, Column>;
  cards: Map<string, Card>;
  participants: Map<string, Participant[]>; // boardId -> participants
  invitations: Map<string, Invitation[]>;
  boardParticipants: Map<string, Set<string>>; // userId -> boardIds
}

function uid(prefix: string): string {
  return `${prefix}_${Math.random().toString(36).slice(2, 11)}`;
}

function nowISO(): string {
  return new Date().toISOString();
}

function createMockDatabase(): MockDatabase {
  return {
    users: new Map(),
    passwords: new Map(),
    boards: new Map(),
    columns: new Map(),
    cards: new Map(),
    participants: new Map(),
    invitations: new Map(),
    boardParticipants: new Map(),
  };
}

// Singleton database — persists across the app session
const db = createMockDatabase();

// Seed a demo user so the app isn't empty on first load
function seedDemoData(): void {
  const demoUser: User = {
    id: uid('user'),
    email: 'demo@example.com',
    name: 'Demo User',
    createdAt: nowISO(),
  };
  db.users.set(demoUser.id, demoUser);
  db.passwords.set(demoUser.email, 'password');

  const board: Board = {
    id: uid('board'),
    name: 'Welcome Board',
    ownerId: demoUser.id,
    ownerName: demoUser.name,
    createdAt: nowISO(),
    updatedAt: nowISO(),
  };
  db.boards.set(board.id, board);

  const participants: Participant[] = [
    {
      userId: demoUser.id,
      email: demoUser.email,
      name: demoUser.name,
      role: 'owner',
      joinedAt: nowISO(),
    },
  ];
  db.participants.set(board.id, participants);
  db.boardParticipants.set(demoUser.id, new Set([board.id]));

  const columns: Column[] = DEFAULT_COLUMNS.map((name, i) => {
    const col: Column = {
      id: uid('col'),
      boardId: board.id,
      name,
      order: i,
      createdAt: nowISO(),
    };
    db.columns.set(col.id, col);
    return col;
  });

  // Add a sample card
  const sampleCard: Card = {
    id: uid('card'),
    boardId: board.id,
    columnId: columns[0].id,
    title: 'Try dragging this card',
    description: 'Drag me to the right to move me between columns.',
    creatorId: demoUser.id,
    creatorName: demoUser.name,
    assigneeId: demoUser.id,
    assigneeName: demoUser.name,
    createdAt: nowISO(),
    updatedAt: nowISO(),
  };
  db.cards.set(sampleCard.id, sampleCard);

  db.invitations.set(board.id, []);
}

seedDemoData();

export { db, uid, nowISO };
export type { MockDatabase };
