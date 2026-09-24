import type { BoardEvent } from '@/types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface PollBoardUpdatesOptions {
  boardId: string;
  since: string;
  token: string;
  onUpdate: (events: BoardEvent[]) => void;
  onError?: (error: Error) => void;
  onRetry?: () => void;
}

export interface PollBoardUpdatesResult {
  stop: () => void;
  updateSince: (newSince: string) => void;
}

export async function pollBoardUpdates(
  options: PollBoardUpdatesOptions
): Promise<PollBoardUpdatesResult> {
  const { boardId, since, token, onUpdate, onError, onRetry } = options;
  
  let isStopped = false;
  let currentSince = since;

  const poll = async () => {
    if (isStopped) return;

    try {
      const url = `${API_BASE_URL}/api/boards/${boardId}/updates?since=${encodeURIComponent(currentSince)}`;
      
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Authentication required');
        } else if (response.status === 403) {
          throw new Error('Not a participant of this board');
        } else {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
      }

      const events: BoardEvent[] = await response.json();
      
      if (events.length > 0) {
        onUpdate(events);
        // Update to the latest timestamp for the next poll
        currentSince = events[events.length - 1].timestamp;
      }

      // Immediately start next poll
      setTimeout(poll, 0);
      
    } catch (error) {
      if (isStopped) return;
      
      if (onError) {
        onError(error as Error);
      }
      
      // Retry after 2 seconds on error
      if (onRetry) {
        onRetry();
      }
      
      setTimeout(poll, 2000);
    }
  };

  // Start polling
  poll();

  return {
    stop: () => {
      isStopped = true;
    },
    updateSince: (newSince: string) => {
      currentSince = newSince;
    },
  };
}