import { nanoid } from 'nanoid';
import type {
  Session,
  SessionParticipant,
  ServiceResult,
  SessionEvent,
} from '../types';
import type { ISessionService } from './interfaces';
import { mockDB } from './mock-db';
import { mockSync } from './mock-sync';

function generateJoinCode(): string {
  return Math.random().toString(36).substring(2, 8).toUpperCase();
}

function delay(ms: number = 100): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function recordEvent(event: SessionEvent): void {
  mockDB.events.push(event);
  mockSync.getChannel<SessionEvent>(`events:${event.sessionId}`).broadcast(event);
}

export class MockSessionService implements ISessionService {
  async createSession(params: {
    title: string;
    description: string;
    interviewerName: string;
  }): Promise<ServiceResult<{ session: Session; participant: SessionParticipant }>> {
    await delay();
    const sessionId = nanoid();
    const participantId = nanoid();
    const now = Date.now();

    const participant: SessionParticipant = {
      id: participantId,
      name: params.interviewerName,
      role: 'interviewer',
      joinedAt: now,
    };

    const session: Session = {
      id: sessionId,
      title: params.title,
      description: params.description,
      joinCode: generateJoinCode(),
      status: 'active',
      createdAt: now,
      participants: [participant],
    };

    mockDB.sessions.set(sessionId, session);
    mockDB.diagrams.set(sessionId, []);

    recordEvent({
      id: nanoid(),
      sessionId,
      type: 'join',
      participantId,
      participantName: participant.name,
      timestamp: now,
    });

    mockSync.getChannel<Session>(`session:${sessionId}`).broadcast(session);

    return { data: { session, participant }, error: null };
  }

  async joinSession(params: {
    joinCode: string;
    candidateName: string;
  }): Promise<ServiceResult<{ session: Session; participant: SessionParticipant }>> {
    await delay();
    let foundSession: Session | null = null;
    for (const session of mockDB.sessions.values()) {
      if (session.joinCode === params.joinCode) {
        foundSession = session;
        break;
      }
    }

    if (!foundSession) {
      return { data: null, error: 'No session found with that join code.' };
    }

    if (foundSession.status === 'completed') {
      return { data: null, error: 'This session has already been completed.' };
    }

    const participantId = nanoid();
    const now = Date.now();
    const participant: SessionParticipant = {
      id: participantId,
      name: params.candidateName,
      role: 'candidate',
      joinedAt: now,
    };

    foundSession.participants.push(participant);
    mockDB.sessions.set(foundSession.id, foundSession);

    recordEvent({
      id: nanoid(),
      sessionId: foundSession.id,
      type: 'join',
      participantId,
      participantName: participant.name,
      timestamp: now,
    });

    mockSync.getChannel<Session>(`session:${foundSession.id}`).broadcast(foundSession);

    return { data: { session: foundSession, participant }, error: null };
  }

  async getSession(sessionId: string): Promise<ServiceResult<Session>> {
    await delay(50);
    const session = mockDB.sessions.get(sessionId);
    if (!session) {
      return { data: null, error: 'Session not found.' };
    }
    return { data: session, error: null };
  }

  async completeSession(sessionId: string): Promise<ServiceResult<Session>> {
    await delay();
    const session = mockDB.sessions.get(sessionId);
    if (!session) {
      return { data: null, error: 'Session not found.' };
    }

    session.status = 'completed';
    mockDB.sessions.set(sessionId, session);

    const now = Date.now();
    recordEvent({
      id: nanoid(),
      sessionId,
      type: 'session-complete',
      participantId: '',
      participantName: '',
      timestamp: now,
    });

    mockSync.getChannel<Session>(`session:${sessionId}`).broadcast(session);

    return { data: session, error: null };
  }

  async subscribeToSession(
    sessionId: string,
    callback: (session: Session) => void,
    options?: { signal?: AbortSignal },
  ): Promise<() => void> {
    const channel = mockSync.getChannel<Session>(`session:${sessionId}`);
    const unsubscribe = channel.subscribe(callback);

    if (options?.signal) {
      options.signal.addEventListener('abort', unsubscribe, { once: true });
    }

    return unsubscribe;
  }
}
