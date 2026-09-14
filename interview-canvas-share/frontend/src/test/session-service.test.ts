import { describe, it, expect, beforeEach } from 'vitest';
import { MockSessionService } from '../services/mock-session';
import { mockDB } from '../services/mock-db';
import { mockSync } from '../services/mock-sync';

describe('MockSessionService', () => {
  let service: MockSessionService;

  beforeEach(() => {
    mockDB.clear();
    mockSync.clearAll();
    service = new MockSessionService();
  });

  describe('createSession', () => {
    it('creates a session with an interviewer participant', async () => {
      const result = await service.createSession({
        title: 'URL Shortener',
        description: 'Design a URL shortening service',
        interviewerName: 'Alice',
      });

      expect(result.error).toBeNull();
      expect(result.data).not.toBeNull();

      const { session, participant } = result.data!;
      expect(session.title).toBe('URL Shortener');
      expect(session.description).toBe('Design a URL shortening service');
      expect(session.status).toBe('active');
      expect(session.joinCode).toHaveLength(6);
      expect(session.participants).toHaveLength(1);
      expect(participant.name).toBe('Alice');
      expect(participant.role).toBe('interviewer');
    });

    it('generates a unique join code', async () => {
      const r1 = await service.createSession({ title: 'A', description: '', interviewerName: 'X' });
      const r2 = await service.createSession({ title: 'B', description: '', interviewerName: 'Y' });
      expect(r1.data!.session.joinCode).not.toBe(r2.data!.session.joinCode);
    });

    it('stores the session in the mock DB', async () => {
      const result = await service.createSession({ title: 'Test', description: '', interviewerName: 'Bob' });
      const stored = mockDB.sessions.get(result.data!.session.id);
      expect(stored).toBeDefined();
      expect(stored!.title).toBe('Test');
    });

    it('records a join event', async () => {
      const result = await service.createSession({ title: 'Test', description: '', interviewerName: 'Bob' });
      const events = mockDB.events.filter((e) => e.sessionId === result.data!.session.id);
      expect(events).toHaveLength(1);
      expect(events[0].type).toBe('join');
      expect(events[0].participantName).toBe('Bob');
    });
  });

  describe('joinSession', () => {
    it('joins an existing session as a candidate', async () => {
      const createResult = await service.createSession({
        title: 'Test',
        description: '',
        interviewerName: 'Alice',
      });
      const joinCode = createResult.data!.session.joinCode;

      const joinResult = await service.joinSession({
        joinCode,
        candidateName: 'Charlie',
      });

      expect(joinResult.error).toBeNull();
      expect(joinResult.data).not.toBeNull();
      expect(joinResult.data!.participant.name).toBe('Charlie');
      expect(joinResult.data!.participant.role).toBe('candidate');
      expect(joinResult.data!.session.participants).toHaveLength(2);
    });

    it('returns an error for an invalid join code', async () => {
      const result = await service.joinSession({
        joinCode: 'INVALID',
        candidateName: 'Charlie',
      });
      expect(result.data).toBeNull();
      expect(result.error).toContain('No session found');
    });

    it('returns an error when joining a completed session', async () => {
      const createResult = await service.createSession({
        title: 'Test',
        description: '',
        interviewerName: 'Alice',
      });
      const sessionId = createResult.data!.session.id;
      await service.completeSession(sessionId);

      const result = await service.joinSession({
        joinCode: createResult.data!.session.joinCode,
        candidateName: 'Charlie',
      });
      expect(result.data).toBeNull();
      expect(result.error).toContain('completed');
    });
  });

  describe('getSession', () => {
    it('returns the session by id', async () => {
      const createResult = await service.createSession({
        title: 'Test',
        description: '',
        interviewerName: 'Alice',
      });
      const sessionId = createResult.data!.session.id;

      const result = await service.getSession(sessionId);
      expect(result.data!.title).toBe('Test');
    });

    it('returns an error for a non-existent session', async () => {
      const result = await service.getSession('nonexistent');
      expect(result.data).toBeNull();
      expect(result.error).toBe('Session not found.');
    });
  });

  describe('completeSession', () => {
    it('marks a session as completed', async () => {
      const createResult = await service.createSession({
        title: 'Test',
        description: '',
        interviewerName: 'Alice',
      });
      const sessionId = createResult.data!.session.id;

      const result = await service.completeSession(sessionId);
      expect(result.data!.status).toBe('completed');
    });

    it('records a session-complete event', async () => {
      const createResult = await service.createSession({
        title: 'Test',
        description: '',
        interviewerName: 'Alice',
      });
      const sessionId = createResult.data!.session.id;
      await service.completeSession(sessionId);

      const events = mockDB.events.filter((e) => e.type === 'session-complete');
      expect(events).toHaveLength(1);
    });
  });

  describe('subscribeToSession', () => {
    it('calls the callback when the session is updated', async () => {
      const createResult = await service.createSession({
        title: 'Test',
        description: '',
        interviewerName: 'Alice',
      });
      const sessionId = createResult.data!.session.id;

      const updates: Session[] = [];
      await service.subscribeToSession(sessionId, (s) => updates.push(s));

      await service.completeSession(sessionId);

      // The first call is the initial broadcast from createSession,
      // the second from completeSession
      expect(updates.length).toBeGreaterThanOrEqual(1);
      const lastUpdate = updates[updates.length - 1];
      expect(lastUpdate.status).toBe('completed');
    });

    it('returns an unsubscribe function', async () => {
      const createResult = await service.createSession({
        title: 'Test',
        description: '',
        interviewerName: 'Alice',
      });
      const sessionId = createResult.data!.session.id;

      const unsub = await service.subscribeToSession(sessionId, () => {});
      expect(typeof unsub).toBe('function');
      unsub();
    });
  });
});

import type { Session } from '../types';
