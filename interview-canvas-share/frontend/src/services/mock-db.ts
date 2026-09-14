import type {
  Session,
  DiagramElement,
  Note,
  SessionEvent,
} from '../types';

interface MockDBShape {
  sessions: Map<string, Session>;
  diagrams: Map<string, DiagramElement[]>;
  notes: Note[];
  events: SessionEvent[];
}

class MockDB {
  private data: MockDBShape = {
    sessions: new Map(),
    diagrams: new Map(),
    notes: [],
    events: [],
  };

  private static instance: MockDB | null = null;

  static getInstance(): MockDB {
    if (!MockDB.instance) {
      MockDB.instance = new MockDB();
    }
    return MockDB.instance;
  }

  static reset(): void {
    MockDB.instance = null;
  }

  get sessions() {
    return this.data.sessions;
  }

  get diagrams() {
    return this.data.diagrams;
  }

  get notes() {
    return this.data.notes;
  }

  get events() {
    return this.data.events;
  }

  clear(): void {
    this.data = {
      sessions: new Map(),
      diagrams: new Map(),
      notes: [],
      events: [],
    };
  }
}

export const mockDB = MockDB.getInstance();
export { MockDB };
