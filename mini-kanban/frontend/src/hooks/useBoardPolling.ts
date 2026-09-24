import { useState, useEffect, useCallback, useRef } from 'react';
import { pollBoardUpdates, type PollBoardUpdatesOptions, type PollBoardUpdatesResult } from '@/services/updates';
import type { BoardEvent } from '@/types';

interface UseBoardPollingOptions {
  boardId: string;
  token: string;
  enabled?: boolean;
  initialSince?: string;
  onUpdate?: (events: BoardEvent[]) => void;
  onError?: (error: Error) => void;
}

export function useBoardPolling(options: UseBoardPollingOptions) {
  const { 
    boardId, 
    token, 
    enabled = true, 
    initialSince = new Date().toISOString(),
    onUpdate,
    onError 
  } = options;
  
  const [lastTimestamp, setLastTimestamp] = useState(initialSince);
  const [isPolling, setIsPolling] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const pollResultRef = useRef<PollBoardUpdatesResult | null>(null);

  const handleUpdate = useCallback((events: BoardEvent[]) => {
    setLastTimestamp(events[events.length - 1].timestamp);
    setError(null);
    
    // Call the user's onUpdate callback if provided
    if (onUpdate) {
      onUpdate(events);
    }
  }, [onUpdate]);

  const handleError = useCallback((err: Error) => {
    setError(err);
    if (onError) {
      onError(err);
    }
  }, [onError]);

  const handleRetry = useCallback(() => {
    // Reset error before retrying
    setError(null);
  }, []);

  // Start/stop polling based on enabled flag
  useEffect(() => {
    if (!enabled) {
      if (pollResultRef.current) {
        pollResultRef.current.stop();
        pollResultRef.current = null;
      }
      setIsPolling(false);
      return;
    }

    if (boardId && token) {
      setIsPolling(true);
      
      const pollOptions: PollBoardUpdatesOptions = {
        boardId,
        since: lastTimestamp,
        token,
        onUpdate: handleUpdate,
        onError: handleError,
        onRetry: handleRetry,
      };

      pollBoardUpdates(pollOptions).then(result => {
        pollResultRef.current = result;
      }).catch(err => {
        setIsPolling(false);
        handleError(err as Error);
      });
    }

    return () => {
      if (pollResultRef.current) {
        pollResultRef.current.stop();
        pollResultRef.current = null;
      }
      setIsPolling(false);
    };
  }, [boardId, token, enabled, lastTimestamp, handleUpdate, handleError, handleRetry]);

  // Update the since timestamp when it changes externally
  useEffect(() => {
    if (pollResultRef.current && enabled) {
      pollResultRef.current.updateSince(lastTimestamp);
    }
  }, [lastTimestamp, enabled]);

  const stopPolling = useCallback(() => {
    if (pollResultRef.current) {
      pollResultRef.current.stop();
      pollResultRef.current = null;
    }
    setIsPolling(false);
  }, []);

  const restartPolling = useCallback(() => {
    stopPolling();
    if (enabled && boardId && token) {
      setIsPolling(true);
      
      const pollOptions: PollBoardUpdatesOptions = {
        boardId,
        since: lastTimestamp,
        token,
        onUpdate: handleUpdate,
        onError: handleError,
        onRetry: handleRetry,
      };

      pollBoardUpdates(pollOptions).then(result => {
        pollResultRef.current = result;
      }).catch(err => {
        setIsPolling(false);
        handleError(err as Error);
      });
    }
  }, [boardId, token, enabled, lastTimestamp, handleUpdate, handleError, handleRetry, stopPolling]);

  return {
    lastTimestamp,
    isPolling,
    error,
    stopPolling,
    restartPolling,
    updateTimestamp: setLastTimestamp,
  };
}