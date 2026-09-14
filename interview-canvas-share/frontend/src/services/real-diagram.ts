import type { IDiagramService } from './interfaces';
import type { ServiceResult } from '../types';
import type { DiagramElement, DiagramState } from '../types';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export class RealDiagramService implements IDiagramService {
  private api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  async getDiagram(sessionId: string): Promise<ServiceResult<DiagramState>> {
    try {
      const response = await this.api.get(`/sessions/${sessionId}/diagram`);
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

  async addElement(
    sessionId: string,
    element: Omit<DiagramElement, 'id'>,
    actorId: string,
  ): Promise<ServiceResult<DiagramElement>> {
    try {
      const response = await this.api.post(`/sessions/${sessionId}/diagram`, {
        sessionId,
        element,
        actorId,
      });
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

  async updateElement(
    sessionId: string,
    elementId: string,
    updates: Partial<DiagramElement>,
    actorId: string,
  ): Promise<ServiceResult<DiagramElement>> {
    try {
      const response = await this.api.put(`/sessions/${sessionId}/diagram`, {
        sessionId,
        elementId,
        updates,
        actorId,
      });
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

  async removeElement(
    sessionId: string,
    elementId: string,
    actorId: string,
  ): Promise<ServiceResult<{ id: string }>> {
    try {
      const response = await this.api.delete(`/sessions/${sessionId}/diagram`, {
        data: {
          sessionId,
          elementId,
          actorId,
        },
      });
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

  async subscribeToDiagram(
    sessionId: string,
    callback: (state: DiagramState) => void,
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
        const result = await this.getDiagram(sessionId);
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