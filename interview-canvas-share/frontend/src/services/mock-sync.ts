type Listener<T> = (data: T) => void;

class MockSyncChannel<T> {
  private listeners = new Set<Listener<T>>();
  private lastValue: T | null = null;

  subscribe(listener: Listener<T>): () => void {
    this.listeners.add(listener);
    if (this.lastValue !== null) {
      listener(this.lastValue);
    }
    return () => {
      this.listeners.delete(listener);
    };
  }

  broadcast(data: T): void {
    this.lastValue = data;
    for (const listener of this.listeners) {
      listener(data);
    }
  }

  clear(): void {
    this.listeners.clear();
    this.lastValue = null;
  }
}

class MockSyncManager {
  private channels = new Map<string, MockSyncChannel<unknown>>();

  getChannel<T>(key: string): MockSyncChannel<T> {
    if (!this.channels.has(key)) {
      this.channels.set(key, new MockSyncChannel<unknown>());
    }
    return this.channels.get(key) as MockSyncChannel<T>;
  }

  clearAll(): void {
    for (const channel of this.channels.values()) {
      channel.clear();
    }
    this.channels.clear();
  }
}

export const mockSync = new MockSyncManager();
