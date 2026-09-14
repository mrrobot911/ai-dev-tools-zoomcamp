export type Role = 'interviewer' | 'candidate';

export type SessionStatus = 'active' | 'completed';

export interface SessionParticipant {
  id: string;
  name: string;
  role: Role;
  joinedAt: number;
}

export interface Session {
  id: string;
  title: string;
  description: string;
  joinCode: string;
  status: SessionStatus;
  createdAt: number;
  participants: SessionParticipant[];
}

export type ElementType = 'box' | 'arrow' | 'text';

export interface DiagramElement {
  id: string;
  type: ElementType;
  // box
  x?: number;
  y?: number;
  width?: number;
  height?: number;
  label?: string;
  // arrow
  fromId?: string;
  toId?: string;
  // text
  text?: string;
}

export interface DiagramState {
  elements: DiagramElement[];
}

export type NoteVisibility = 'private' | 'shared';

export interface Note {
  id: string;
  sessionId: string;
  authorId: string;
  authorName: string;
  content: string;
  visibility: NoteVisibility;
  createdAt: number;
  updatedAt: number;
}

export type EventType = 'join' | 'leave' | 'element-add' | 'element-update' | 'element-remove' | 'note-add' | 'note-update' | 'note-remove' | 'session-complete';

export interface SessionEvent {
  id: string;
  sessionId: string;
  type: EventType;
  participantId: string;
  participantName: string;
  timestamp: number;
  payload?: Record<string, unknown>;
}

export interface ServiceResult<T> {
  data: T | null;
  error: string | null;
}

export interface ServiceError {
  error: string;
}
