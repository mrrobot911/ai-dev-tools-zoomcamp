import type {
  Session,
  SessionParticipant,
  DiagramElement,
  DiagramState,
  Note,
  NoteVisibility,
  SessionEvent,
  ServiceResult,
} from '../types';

export interface ISessionService {
  createSession(params: {
    title: string;
    description: string;
    interviewerName: string;
  }): Promise<ServiceResult<{ session: Session; participant: SessionParticipant }>>;

  joinSession(params: {
    joinCode: string;
    candidateName: string;
  }): Promise<ServiceResult<{ session: Session; participant: SessionParticipant }>>;

  getSession(sessionId: string): Promise<ServiceResult<Session>>;

  completeSession(sessionId: string): Promise<ServiceResult<Session>>;

  subscribeToSession(
    sessionId: string,
    callback: (session: Session) => void,
  options?: { signal?: AbortSignal },
  ): Promise<() => void>;
}

export interface IDiagramService {
  getDiagram(sessionId: string): Promise<ServiceResult<DiagramState>>;

  addElement(
    sessionId: string,
    element: Omit<DiagramElement, 'id'>,
  actorId: string,
  ): Promise<ServiceResult<DiagramElement>>;

  updateElement(
    sessionId: string,
    elementId: string,
    updates: Partial<DiagramElement>,
    actorId: string,
  ): Promise<ServiceResult<DiagramElement>>;

  removeElement(
    sessionId: string,
    elementId: string,
    actorId: string,
  ): Promise<ServiceResult<{ id: string }>>;

  subscribeToDiagram(
    sessionId: string,
    callback: (state: DiagramState) => void,
    options?: { signal?: AbortSignal },
  ): Promise<() => void>;
}

export interface INoteService {
  getNotes(sessionId: string, participantId: string): Promise<ServiceResult<Note[]>>;

  addNote(params: {
    sessionId: string;
    authorId: string;
    authorName: string;
    content: string;
    visibility: NoteVisibility;
  }): Promise<ServiceResult<Note>>;

  updateNote(
    noteId: string,
    updates: { content?: string; visibility?: NoteVisibility },
    actorId: string,
  ): Promise<ServiceResult<Note>>;

  removeNote(noteId: string, actorId: string): Promise<ServiceResult<{ id: string }>>;

  subscribeToNotes(
    sessionId: string,
    participantId: string,
    callback: (notes: Note[]) => void,
    options?: { signal?: AbortSignal },
  ): Promise<() => void>;
}

export interface IEventService {
  getEvents(sessionId: string): Promise<ServiceResult<SessionEvent[]>>;

  subscribeToEvents(
    sessionId: string,
    callback: (event: SessionEvent) => void,
    options?: { signal?: AbortSignal },
  ): Promise<() => void>;
}

export interface IAuthService {
  getCurrentParticipant(): SessionParticipant | null;
  setCurrentParticipant(participant: SessionParticipant | null): void;
  clearCurrentParticipant(): void;
}

export interface Services {
  session: ISessionService;
  diagram: IDiagramService;
  note: INoteService;
  event: IEventService;
  auth: IAuthService;
}
