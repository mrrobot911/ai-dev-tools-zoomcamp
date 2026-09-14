import type { IEventService } from './interfaces';
import type { ServiceResult } from '../types';
import type { SessionEvent } from '../types';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export class RealEventService implements IEventService {
  private api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  async getEvents(sessionId: string): Promise<ServiceResult<SessionEvent[]>> {
    try {
      const response = await this.api.get(`/sessions/${sessionId}/events`);
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

  async subscribeToEvents(
    sessionId: string,
    callback: (event: SessionEvent) => void,
    options?: { signal?: AbortSignal },
  ): Promise<() => void> {
    // For real backend, we would use WebSockets or Server-Sent Events
    // For now, we'll implement polling as a fallback
    let lastEventId: string | null = null;
    
    const interval = setInterval(async () => {
      if (options?.signal?.aborted) {
        clearInterval(interval);
        return;
      }

      try {
        const result = await this.getEvents(sessionId);
        if (result.data && !result.error) {
          const newEvents = result.data.filter((event: SessionEvent) => 
            !lastEventId || event.timestamp > new Date(lastEventId).getTime()
          );
          
          if (newEvents.length > 0) {
            newEvents.forEach((event: SessionEvent) => {
              callback(event);
              lastEventId = event.id;
            });
          }
        }
      } catch (error) {
        // Silently ignore polling errors
      }
    }, 2000); // Poll every 2 seconds

    return () => clearInterval(interval);
  }
}