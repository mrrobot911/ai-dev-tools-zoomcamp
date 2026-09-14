import { describe, it, expect, beforeEach } from 'vitest';
import { MockNoteService } from '../services/mock-note';
import { MockSessionService } from '../services/mock-session';
import { mockDB } from '../services/mock-db';
import { mockSync } from '../services/mock-sync';

describe('MockNoteService', () => {
  let noteService: MockNoteService;
  let sessionService: MockSessionService;
  let sessionId: string;
  let interviewerId: string;
  let candidateId: string;

  beforeEach(async () => {
    mockDB.clear();
    mockSync.clearAll();
    noteService = new MockNoteService();
    sessionService = new MockSessionService();

    const createResult = await sessionService.createSession({
      title: 'Test',
      description: '',
      interviewerName: 'Alice',
    });
    sessionId = createResult.data!.session.id;
    interviewerId = createResult.data!.participant.id;

    const joinResult = await sessionService.joinSession({
      joinCode: createResult.data!.session.joinCode,
      candidateName: 'Bob',
    });
    candidateId = joinResult.data!.participant.id;
  });

  describe('addNote', () => {
    it('creates a note with the given visibility', async () => {
      const result = await noteService.addNote({
        sessionId,
        authorId: interviewerId,
        authorName: 'Alice',
        content: 'Candidate struggled with scaling',
        visibility: 'private',
      });

      expect(result.data!.content).toBe('Candidate struggled with scaling');
      expect(result.data!.visibility).toBe('private');
      expect(result.data!.id).toBeDefined();
    });

    it('records a note-add event', async () => {
      await noteService.addNote({
        sessionId,
        authorId: interviewerId,
        authorName: 'Alice',
        content: 'Test note',
        visibility: 'shared',
      });

      const events = mockDB.events.filter((e) => e.type === 'note-add');
      expect(events).toHaveLength(1);
    });
  });

  describe('getNotes', () => {
    it('returns only private notes for the author and all shared notes', async () => {
      await noteService.addNote({
        sessionId,
        authorId: interviewerId,
        authorName: 'Alice',
        content: 'Private from Alice',
        visibility: 'private',
      });

      await noteService.addNote({
        sessionId,
        authorId: interviewerId,
        authorName: 'Alice',
        content: 'Shared from Alice',
        visibility: 'shared',
      });

      await noteService.addNote({
        sessionId,
        authorId: candidateId,
        authorName: 'Bob',
        content: 'Private from Bob',
        visibility: 'private',
      });

      const interviewerNotes = await noteService.getNotes(sessionId, interviewerId);
      expect(interviewerNotes.data).toHaveLength(2);
      expect(interviewerNotes.data!.map((n) => n.content).sort()).toEqual(
        ['Private from Alice', 'Shared from Alice'],
      );

      const candidateNotes = await noteService.getNotes(sessionId, candidateId);
      expect(candidateNotes.data).toHaveLength(2);
      expect(candidateNotes.data!.map((n) => n.content).sort()).toEqual(
        ['Private from Bob', 'Shared from Alice'],
      );
    });
  });

  describe('updateNote', () => {
    it('updates the note content', async () => {
      const addResult = await noteService.addNote({
        sessionId,
        authorId: interviewerId,
        authorName: 'Alice',
        content: 'Original',
        visibility: 'private',
      });

      const updateResult = await noteService.updateNote(
        addResult.data!.id,
        { content: 'Updated' },
        interviewerId,
      );

      expect(updateResult.data!.content).toBe('Updated');
    });

    it('prevents updating another user\'s note', async () => {
      const addResult = await noteService.addNote({
        sessionId,
        authorId: interviewerId,
        authorName: 'Alice',
        content: 'Alice note',
        visibility: 'private',
      });

      const result = await noteService.updateNote(
        addResult.data!.id,
        { content: 'Hacked' },
        candidateId,
      );

      expect(result.data).toBeNull();
      expect(result.error).toContain('own notes');
    });

    it('can change visibility from private to shared', async () => {
      const addResult = await noteService.addNote({
        sessionId,
        authorId: interviewerId,
        authorName: 'Alice',
        content: 'Secret',
        visibility: 'private',
      });

      const result = await noteService.updateNote(
        addResult.data!.id,
        { visibility: 'shared' },
        interviewerId,
      );

      expect(result.data!.visibility).toBe('shared');
    });
  });

  describe('removeNote', () => {
    it('removes a note', async () => {
      const addResult = await noteService.addNote({
        sessionId,
        authorId: interviewerId,
        authorName: 'Alice',
        content: 'To be deleted',
        visibility: 'private',
      });

      await noteService.removeNote(addResult.data!.id, interviewerId);
      expect(mockDB.notes).toHaveLength(0);
    });

    it('prevents deleting another user\'s note', async () => {
      const addResult = await noteService.addNote({
        sessionId,
        authorId: interviewerId,
        authorName: 'Alice',
        content: 'Alice note',
        visibility: 'private',
      });

      const result = await noteService.removeNote(addResult.data!.id, candidateId);
      expect(result.data).toBeNull();
      expect(result.error).toContain('own notes');
    });
  });

  describe('subscribeToNotes', () => {
    it('calls the callback when notes change', async () => {
      const notesUpdates: import('../types').Note[][] = [];
      await noteService.subscribeToNotes(sessionId, interviewerId, (n) => notesUpdates.push(n));

      await noteService.addNote({
        sessionId,
        authorId: interviewerId,
        authorName: 'Alice',
        content: 'Test',
        visibility: 'private',
      });

      const lastUpdate = notesUpdates[notesUpdates.length - 1];
      expect(lastUpdate).toHaveLength(1);
      expect(lastUpdate[0].content).toBe('Test');
    });
  });
});
