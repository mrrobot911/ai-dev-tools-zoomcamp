import { describe, it, expect, beforeEach } from 'vitest';
import { MockDiagramService } from '../services/mock-diagram';
import { MockSessionService } from '../services/mock-session';
import { mockDB } from '../services/mock-db';
import { mockSync } from '../services/mock-sync';

describe('MockDiagramService', () => {
  let diagramService: MockDiagramService;
  let sessionService: MockSessionService;
  let sessionId: string;
  let actorId: string;

  beforeEach(async () => {
    mockDB.clear();
    mockSync.clearAll();
    diagramService = new MockDiagramService();
    sessionService = new MockSessionService();

    const result = await sessionService.createSession({
      title: 'Test',
      description: '',
      interviewerName: 'Alice',
    });
    sessionId = result.data!.session.id;
    actorId = result.data!.participant.id;
  });

  describe('getDiagram', () => {
    it('returns an empty diagram for a new session', async () => {
      const result = await diagramService.getDiagram(sessionId);
      expect(result.data!.elements).toHaveLength(0);
    });
  });

  describe('addElement', () => {
    it('adds a box element with a generated id', async () => {
      const result = await diagramService.addElement(sessionId, {
        type: 'box',
        x: 100,
        y: 200,
        width: 140,
        height: 60,
        label: 'API Gateway',
      }, actorId);

      expect(result.data!.id).toBeDefined();
      expect(result.data!.type).toBe('box');
      expect(result.data!.label).toBe('API Gateway');
      expect(result.data!.x).toBe(100);
    });

    it('stores the element in the mock DB', async () => {
      await diagramService.addElement(sessionId, {
        type: 'box',
        x: 0,
        y: 0,
        width: 100,
        height: 50,
        label: 'Test',
      }, actorId);

      const stored = mockDB.diagrams.get(sessionId);
      expect(stored).toHaveLength(1);
    });

    it('records an element-add event', async () => {
      await diagramService.addElement(sessionId, {
        type: 'box',
        x: 0,
        y: 0,
        width: 100,
        height: 50,
        label: 'Test',
      }, actorId);

      const events = mockDB.events.filter((e) => e.type === 'element-add');
      expect(events).toHaveLength(1);
    });
  });

  describe('updateElement', () => {
    it('updates an existing element', async () => {
      const addResult = await diagramService.addElement(sessionId, {
        type: 'box',
        x: 0,
        y: 0,
        width: 100,
        height: 50,
        label: 'Original',
      }, actorId);

      const updateResult = await diagramService.updateElement(
        sessionId,
        addResult.data!.id,
        { label: 'Updated' },
        actorId,
      );

      expect(updateResult.data!.label).toBe('Updated');
    });

    it('returns an error for a non-existent element', async () => {
      const result = await diagramService.updateElement(
        sessionId,
        'nonexistent',
        { label: 'X' },
        actorId,
      );
      expect(result.data).toBeNull();
      expect(result.error).toBe('Element not found.');
    });
  });

  describe('removeElement', () => {
    it('removes an element', async () => {
      const addResult = await diagramService.addElement(sessionId, {
        type: 'box',
        x: 0,
        y: 0,
        width: 100,
        height: 50,
        label: 'Test',
      }, actorId);

      await diagramService.removeElement(sessionId, addResult.data!.id, actorId);

      const stored = mockDB.diagrams.get(sessionId);
      expect(stored).toHaveLength(0);
    });

    it('records an element-remove event', async () => {
      const addResult = await diagramService.addElement(sessionId, {
        type: 'box',
        x: 0,
        y: 0,
        width: 100,
        height: 50,
        label: 'Test',
      }, actorId);

      await diagramService.removeElement(sessionId, addResult.data!.id, actorId);
      const events = mockDB.events.filter((e) => e.type === 'element-remove');
      expect(events).toHaveLength(1);
    });
  });

  describe('subscribeToDiagram', () => {
    it('calls the callback when the diagram changes', async () => {
      const states: import('../types').DiagramState[] = [];
      await diagramService.subscribeToDiagram(sessionId, (s) => states.push(s));

      await diagramService.addElement(sessionId, {
        type: 'box',
        x: 0,
        y: 0,
        width: 100,
        height: 50,
        label: 'Test',
      }, actorId);

      const lastState = states[states.length - 1];
      expect(lastState.elements).toHaveLength(1);
    });
  });
});
