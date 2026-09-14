import { describe, it, expect, beforeEach } from 'vitest';
import { getServices } from '../services';
import { mockDB } from '../services/mock-db';
import { mockSync } from '../services/mock-sync';

describe('Integration: Full interview flow', () => {
  beforeEach(() => {
    mockDB.clear();
    mockSync.clearAll();
  });

  it('end-to-end: create session, join, add diagram elements, add notes, complete', async () => {
    const services = getServices();

    // 1. Interviewer creates a session
    const createResult = await services.session.createSession({
      title: 'Design a URL Shortener',
      description: 'Scale to 100M URLs per day',
      interviewerName: 'Alice',
    });
    expect(createResult.error).toBeNull();
    const { session, participant: interviewer } = createResult.data!;

    // 2. Candidate joins
    const joinResult = await services.session.joinSession({
      joinCode: session.joinCode,
      candidateName: 'Bob',
    });
    expect(joinResult.error).toBeNull();
    const { participant: candidate } = joinResult.data!;
    expect(joinResult.data!.session.participants).toHaveLength(2);

    // 3. Interviewer adds diagram elements
    const box1 = await services.diagram.addElement(session.id, {
      type: 'box',
      x: 100,
      y: 100,
      width: 140,
      height: 60,
      label: 'Load Balancer',
    }, interviewer.id);
    expect(box1.data!.id).toBeDefined();

    const box2 = await services.diagram.addElement(session.id, {
      type: 'box',
      x: 300,
      y: 100,
      width: 140,
      height: 60,
      label: 'App Server',
    }, interviewer.id);

    const arrow = await services.diagram.addElement(session.id, {
      type: 'arrow',
      fromId: box1.data!.id,
      toId: box2.data!.id,
    }, interviewer.id);
    expect(arrow.data!.type).toBe('arrow');

    // 4. Candidate adds a shared note
    const noteResult = await services.note.addNote({
      sessionId: session.id,
      authorId: candidate.id,
      authorName: 'Bob',
      content: 'Should we use a CDN?',
      visibility: 'shared',
    });
    expect(noteResult.data!.content).toBe('Should we use a CDN?');

    // 5. Interviewer adds a private note
    await services.note.addNote({
      sessionId: session.id,
      authorId: interviewer.id,
      authorName: 'Alice',
      content: 'Candidate asks good questions',
      visibility: 'private',
    });

    // 6. Both can see shared notes, only author sees private
    const interviewerNotes = await services.note.getNotes(session.id, interviewer.id);
    expect(interviewerNotes.data).toHaveLength(2);

    const candidateNotes = await services.note.getNotes(session.id, candidate.id);
    expect(candidateNotes.data).toHaveLength(1);
    expect(candidateNotes.data![0].content).toBe('Should we use a CDN?');

    // 7. Diagram has 3 elements
    const diagram = await services.diagram.getDiagram(session.id);
    expect(diagram.data!.elements).toHaveLength(3);

    // 8. Complete the session
    const completeResult = await services.session.completeSession(session.id);
    expect(completeResult.data!.status).toBe('completed');

    // 9. Events recorded
    const events = await services.event.getEvents(session.id);
    const eventTypes = events.data!.map((e) => e.type);
    expect(eventTypes).toContain('join');
    expect(eventTypes).toContain('element-add');
    expect(eventTypes).toContain('note-add');
    expect(eventTypes).toContain('session-complete');
  });

  it('real-time sync: diagram updates are pushed to subscribers', async () => {
    const services = getServices();

    const createResult = await services.session.createSession({
      title: 'Test',
      description: '',
      interviewerName: 'Alice',
    });
    const sessionId = createResult.data!.session.id;
    const actorId = createResult.data!.participant.id;

    const receivedStates: import('../types').DiagramState[] = [];
    await services.diagram.subscribeToDiagram(sessionId, (s) => receivedStates.push(s));

    await services.diagram.addElement(sessionId, {
      type: 'box',
      x: 0,
      y: 0,
      width: 100,
      height: 50,
      label: 'Synced Box',
    }, actorId);

    // The subscriber should have received at least one update with the new element
    const lastState = receivedStates[receivedStates.length - 1];
    expect(lastState.elements).toHaveLength(1);
    expect(lastState.elements[0].label).toBe('Synced Box');
  });

  it('real-time sync: session status updates are pushed to subscribers', async () => {
    const services = getServices();

    const createResult = await services.session.createSession({
      title: 'Test',
      description: '',
      interviewerName: 'Alice',
    });
    const sessionId = createResult.data!.session.id;

    const receivedSessions: import('../types').Session[] = [];
    await services.session.subscribeToSession(sessionId, (s) => receivedSessions.push(s));

    await services.session.completeSession(sessionId);

    const lastSession = receivedSessions[receivedSessions.length - 1];
    expect(lastSession.status).toBe('completed');
  });

  it('real-time sync: notes are pushed to the correct participants', async () => {
    const services = getServices();

    const createResult = await services.session.createSession({
      title: 'Test',
      description: '',
      interviewerName: 'Alice',
    });
    const sessionId = createResult.data!.session.id;
    const interviewerId = createResult.data!.participant.id;

    const joinResult = await services.session.joinSession({
      joinCode: createResult.data!.session.joinCode,
      candidateName: 'Bob',
    });
    const candidateId = joinResult.data!.participant.id;

    const interviewerNotesUpdates: import('../types').Note[][] = [];
    const candidateNotesUpdates: import('../types').Note[][] = [];

    await services.note.subscribeToNotes(sessionId, interviewerId, (n) => interviewerNotesUpdates.push(n));
    await services.note.subscribeToNotes(sessionId, candidateId, (n) => candidateNotesUpdates.push(n));

    // Interviewer adds a private note
    await services.note.addNote({
      sessionId,
      authorId: interviewerId,
      authorName: 'Alice',
      content: 'Private thought',
      visibility: 'private',
    });

    // Interviewer should see it, candidate should not
    const lastInterviewerNotes = interviewerNotesUpdates[interviewerNotesUpdates.length - 1];
    const lastCandidateNotes = candidateNotesUpdates[candidateNotesUpdates.length - 1];

    expect(lastInterviewerNotes).toHaveLength(1);
    expect(lastCandidateNotes).toHaveLength(0);
  });
});
