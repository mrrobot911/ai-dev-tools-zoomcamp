import { describe, it, expect, beforeEach } from 'vitest';
import { MockAuthService } from '../services/mock-auth';
import type { SessionParticipant } from '../types';

describe('MockAuthService', () => {
  let service: MockAuthService;

  beforeEach(() => {
    localStorage.clear();
    service = new MockAuthService();
  });

  it('returns null when no participant is stored', () => {
    expect(service.getCurrentParticipant()).toBeNull();
  });

  it('stores and retrieves a participant', () => {
    const participant: SessionParticipant = {
      id: 'p1',
      name: 'Alice',
      role: 'interviewer',
      joinedAt: 1000,
    };

    service.setCurrentParticipant(participant);
    const retrieved = service.getCurrentParticipant();
    expect(retrieved).toEqual(participant);
  });

  it('clears the stored participant', () => {
    const participant: SessionParticipant = {
      id: 'p1',
      name: 'Alice',
      role: 'interviewer',
      joinedAt: 1000,
    };

    service.setCurrentParticipant(participant);
    service.clearCurrentParticipant();
    expect(service.getCurrentParticipant()).toBeNull();
  });

  it('handles null in setCurrentParticipant', () => {
    service.setCurrentParticipant(null);
    expect(service.getCurrentParticipant()).toBeNull();
  });
});
