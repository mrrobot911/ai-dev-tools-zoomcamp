import type { ServiceResult, SessionEvent } from '../types';
import type { IEventService } from './interfaces';
import { mockDB } from './mock-db';
import { mockSync } from './mock-sync';

function delay(ms: number = 50): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export class MockEventService implements IEventService {
  async getEvents(sessionId: string): Promise<ServiceResult<SessionEvent[]>> {
    await delay();
    const events = mockDB.events.filter((e) => e.sessionId === sessionId);
    return { data: events, error: null };
  }

  async subscribeToEvents(
    sessionId: string,
    callback: (event: SessionEvent) => void,
    options?: { signal?: AbortSignal },
  ): Promise<() => void> {
    const channel = mockSync.getChannel<SessionEvent>(`events:${sessionId}`);
    const unsubscribe = channel.subscribe(callback);

    if (options?.signal) {
      options.signal.addEventListener('abort', unsubscribe, { once: true });
    }

    return unsubscribe;
  }
}
