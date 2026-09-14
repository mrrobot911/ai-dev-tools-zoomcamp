import { nanoid } from 'nanoid';
import type {
  DiagramElement,
  DiagramState,
  ServiceResult,
  SessionEvent,
} from '../types';
import type { IDiagramService } from './interfaces';
import { mockDB } from './mock-db';
import { mockSync } from './mock-sync';

function delay(ms: number = 80): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function broadcastDiagram(sessionId: string): void {
  const elements = mockDB.diagrams.get(sessionId) ?? [];
  mockSync.getChannel<DiagramState>(`diagram:${sessionId}`).broadcast({ elements });
}

function recordEvent(
  sessionId: string,
  type: SessionEvent['type'],
  participantId: string,
  participantName: string,
  payload?: Record<string, unknown>,
): void {
  const event: SessionEvent = {
    id: nanoid(),
    sessionId,
    type,
    participantId,
    participantName,
    timestamp: Date.now(),
    payload,
  };
  mockDB.events.push(event);
  mockSync.getChannel<SessionEvent>(`events:${sessionId}`).broadcast(event);
}

export class MockDiagramService implements IDiagramService {
  async getDiagram(sessionId: string): Promise<ServiceResult<DiagramState>> {
    await delay(50);
    const elements = mockDB.diagrams.get(sessionId) ?? [];
    return { data: { elements }, error: null };
  }

  async addElement(
    sessionId: string,
    element: Omit<DiagramElement, 'id'>,
    actorId: string,
  ): Promise<ServiceResult<DiagramElement>> {
    await delay();
    const elements = mockDB.diagrams.get(sessionId) ?? [];
    const newElement: DiagramElement = { ...element, id: nanoid() };
    elements.push(newElement);
    mockDB.diagrams.set(sessionId, elements);

    broadcastDiagram(sessionId);
    recordEvent(sessionId, 'element-add', actorId, '', { elementId: newElement.id });

    return { data: newElement, error: null };
  }

  async updateElement(
    sessionId: string,
    elementId: string,
    updates: Partial<DiagramElement>,
    actorId: string,
  ): Promise<ServiceResult<DiagramElement>> {
    await delay(50);
    const elements = mockDB.diagrams.get(sessionId) ?? [];
    const index = elements.findIndex((e) => e.id === elementId);
    if (index === -1) {
      return { data: null, error: 'Element not found.' };
    }

    elements[index] = { ...elements[index], ...updates, id: elementId };
    mockDB.diagrams.set(sessionId, elements);

    broadcastDiagram(sessionId);
    recordEvent(sessionId, 'element-update', actorId, '', { elementId });

    return { data: elements[index], error: null };
  }

  async removeElement(
    sessionId: string,
    elementId: string,
    actorId: string,
  ): Promise<ServiceResult<{ id: string }>> {
    await delay();
    const elements = mockDB.diagrams.get(sessionId) ?? [];
    const filtered = elements.filter((e) => e.id !== elementId);
    mockDB.diagrams.set(sessionId, filtered);

    broadcastDiagram(sessionId);
    recordEvent(sessionId, 'element-remove', actorId, '', { elementId });

    return { data: { id: elementId }, error: null };
  }

  async subscribeToDiagram(
    sessionId: string,
    callback: (state: DiagramState) => void,
    options?: { signal?: AbortSignal },
  ): Promise<() => void> {
    const channel = mockSync.getChannel<DiagramState>(`diagram:${sessionId}`);
    const unsubscribe = channel.subscribe(callback);

    if (options?.signal) {
      options.signal.addEventListener('abort', unsubscribe, { once: true });
    }

    return unsubscribe;
  }
}
