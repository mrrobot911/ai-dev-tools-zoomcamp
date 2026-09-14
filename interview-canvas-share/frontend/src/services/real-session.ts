import type { ISessionService } from './interfaces';
import type { ServiceResult } from '../types';
import type { Session, SessionParticipant } from '../types';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export class RealSessionService implements ISessionService {
  private api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  async createSession(params: {
    title: string;
    description: string;
    interviewerName: string;
  }): Promise<ServiceResult<{ session: Session; participant: SessionParticipant }>> {
    try {
      const response = await this.api.post('/sessions', params);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        return {
          data: null,
          error: error.response?.data?.error || error.message,
        };
      }
      return {
        data: null,
        error: 'Unknown error occurred',
      };
    }
  }

  async joinSession(params: {
    joinCode: string;
    candidateName: string;
  }): Promise<ServiceResult<{ session: Session; participant: SessionParticipant }>> {
    try {
      const response = await this.api.post('/sessions/join', params);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        return {
          data: null,
          error: error.response?.data?.error || error.message,
        };
      }
      return {
        data: null,
        error: 'Unknown error occurred',
      };
    }
  }

  async getSession(sessionId: string): Promise<ServiceResult<Session>> {
    try {
      const response = await this.api.get(`/sessions/${sessionId}`);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        return {
          data: null,
          error: error.response?.data?.error || error.message,
        };
      }
      return {
        data: null,
        error: 'Unknown error occurred',
      };
    }
  }

  async completeSession(sessionId: string): Promise<ServiceResult<Session>> {
    try {
      const response = await this.api.patch(`/sessions/${sessionId}`);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        return {
          data: null,
          error: error.response?.data?.error || error.message,
        };
      }
      return {
        data: null,
        error: 'Unknown error occurred',
      };
    }
  }

  async subscribeToSession(
    sessionId: string,
    callback: (session: Session) => void,
    options?: { signal?: AbortSignal },
  ): Promise<() => void> {
    // For real backend, we would use WebSockets or Server-Sent Events
    // For now, we'll implement polling as a fallback
    const interval = setInterval(async () => {
      if (options?.signal?.aborted) {
        clearInterval(interval);
        return;
      }

      try {
        const result = await this.getSession(sessionId);
        if (result.data && !result.error) {
          callback(result.data);
        }
      } catch (error) {
        // Silently ignore polling errors
      }
    }, 2000); // Poll every 2 seconds

    return () => clearInterval(interval);
  }
}