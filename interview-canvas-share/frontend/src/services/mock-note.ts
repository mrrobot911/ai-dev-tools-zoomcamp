import { nanoid } from 'nanoid';
import type {
  Note,
  NoteVisibility,
  ServiceResult,
  SessionEvent,
} from '../types';
import type { INoteService } from './interfaces';
import { mockDB } from './mock-db';
import { mockSync } from './mock-sync';

function delay(ms: number = 80): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function filterNotesForParticipant(sessionId: string, participantId: string): Note[] {
  return mockDB.notes.filter(
    (n) =>
      n.sessionId === sessionId &&
      (n.visibility === 'shared' || n.authorId === participantId),
  );
}

function broadcastNotes(sessionId: string, participantId: string): void {
  const notes = filterNotesForParticipant(sessionId, participantId);
  mockSync.getChannel<Note[]>(`notes:${sessionId}:${participantId}`).broadcast(notes);
}

function broadcastAllParticipants(sessionId: string): void {
  const session = mockDB.sessions.get(sessionId);
  if (!session) return;
  for (const participant of session.participants) {
    broadcastNotes(sessionId, participant.id);
  }
}

function recordEvent(
  sessionId: string,
  type: SessionEvent['type'],
  participantId: string,
  participantName: string,
): void {
  const event: SessionEvent = {
    id: nanoid(),
    sessionId,
    type,
    participantId,
    participantName,
    timestamp: Date.now(),
  };
  mockDB.events.push(event);
  mockSync.getChannel<SessionEvent>(`events:${sessionId}`).broadcast(event);
}

export class MockNoteService implements INoteService {
  async getNotes(
    sessionId: string,
    participantId: string,
  ): Promise<ServiceResult<Note[]>> {
    await delay(50);
    const notes = filterNotesForParticipant(sessionId, participantId);
    return { data: notes, error: null };
  }

  async addNote(params: {
    sessionId: string;
    authorId: string;
    authorName: string;
    content: string;
    visibility: NoteVisibility;
  }): Promise<ServiceResult<Note>> {
    await delay();
    const now = Date.now();
    const note: Note = {
      id: nanoid(),
      sessionId: params.sessionId,
      authorId: params.authorId,
      authorName: params.authorName,
      content: params.content,
      visibility: params.visibility,
      createdAt: now,
      updatedAt: now,
    };

    mockDB.notes.push(note);
    broadcastAllParticipants(params.sessionId);
    recordEvent(params.sessionId, 'note-add', params.authorId, params.authorName);

    return { data: note, error: null };
  }

  async updateNote(
    noteId: string,
    updates: { content?: string; visibility?: NoteVisibility },
    actorId: string,
  ): Promise<ServiceResult<Note>> {
    await delay(50);
    const index = mockDB.notes.findIndex((n) => n.id === noteId);
    if (index === -1) {
      return { data: null, error: 'Note not found.' };
    }

    if (mockDB.notes[index].authorId !== actorId) {
      return { data: null, error: 'You can only edit your own notes.' };
    }

    mockDB.notes[index] = {
      ...mockDB.notes[index],
      ...updates,
      updatedAt: Date.now(),
    };

    broadcastAllParticipants(mockDB.notes[index].sessionId);
    recordEvent(
      mockDB.notes[index].sessionId,
      'note-update',
      actorId,
      mockDB.notes[index].authorName,
    );

    return { data: mockDB.notes[index], error: null };
  }

  async removeNote(
    noteId: string,
    actorId: string,
  ): Promise<ServiceResult<{ id: string }>> {
    await delay();
    const index = mockDB.notes.findIndex((n) => n.id === noteId);
    if (index === -1) {
      return { data: null, error: 'Note not found.' };
    }

    if (mockDB.notes[index].authorId !== actorId) {
      return { data: null, error: 'You can only delete your own notes.' };
    }

    const sessionId = mockDB.notes[index].sessionId;
    const authorName = mockDB.notes[index].authorName;
    mockDB.notes.splice(index, 1);

    broadcastAllParticipants(sessionId);
    recordEvent(sessionId, 'note-remove', actorId, authorName);

    return { data: { id: noteId }, error: null };
  }

  async subscribeToNotes(
    sessionId: string,
    participantId: string,
    callback: (notes: Note[]) => void,
    options?: { signal?: AbortSignal },
  ): Promise<() => void> {
    const channel = mockSync.getChannel<Note[]>(`notes:${sessionId}:${participantId}`);
    const unsubscribe = channel.subscribe(callback);

    if (options?.signal) {
      options.signal.addEventListener('abort', unsubscribe, { once: true });
    }

    return unsubscribe;
  }
}
