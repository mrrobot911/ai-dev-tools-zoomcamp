import type { INoteService } from './interfaces';
import type { ServiceResult } from '../types';
import type { Note, NoteVisibility } from '../types';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export class RealNoteService implements INoteService {
  private api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  async getNotes(sessionId: string, participantId: string): Promise<ServiceResult<Note[]>> {
    try {
      const response = await this.api.get(`/sessions/${sessionId}/notes`, {
        params: { participantId },
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

  async addNote(params: {
    sessionId: string;
    authorId: string;
    authorName: string;
    content: string;
    visibility: NoteVisibility;
  }): Promise<ServiceResult<Note>> {
    try {
      const response = await this.api.post(`/sessions/${params.sessionId}/notes`, params);
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

  async updateNote(
    noteId: string,
    updates: { content?: string; visibility?: NoteVisibility },
    actorId: string,
  ): Promise<ServiceResult<Note>> {
    try {
      const response = await this.api.patch(`/notes/${noteId}`, {
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

  async removeNote(noteId: string, actorId: string): Promise<ServiceResult<{ id: string }>> {
    try {
      const response = await this.api.delete(`/notes/${noteId}`, {
        data: { actorId },
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

  async subscribeToNotes(
    sessionId: string,
    participantId: string,
    callback: (notes: Note[]) => void,
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
        const result = await this.getNotes(sessionId, participantId);
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