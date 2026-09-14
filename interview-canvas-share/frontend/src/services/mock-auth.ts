import type { SessionParticipant } from '../types';
import type { IAuthService } from './interfaces';

const STORAGE_KEY = 'sdi_participant';

export class MockAuthService implements IAuthService {
  getCurrentParticipant(): SessionParticipant | null {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return null;
      return JSON.parse(raw) as SessionParticipant;
    } catch {
      return null;
    }
  }

  setCurrentParticipant(participant: SessionParticipant | null): void {
    try {
      if (participant) {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(participant));
      } else {
        localStorage.removeItem(STORAGE_KEY);
      }
    } catch {
      // ignore storage errors
    }
  }

  clearCurrentParticipant(): void {
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch {
      // ignore
    }
  }
}
