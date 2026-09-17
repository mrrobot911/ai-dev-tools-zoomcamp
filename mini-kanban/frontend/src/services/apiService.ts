import type {
  User,
  Board,
  Column,
  Card,
  Invitation,
  BoardWithDetails,
} from '@/types';
import type {
  KanbanService,
  RegisterInput,
  LoginInput,
  CreateBoardInput,
  UpdateBoardInput,
  CreateColumnInput,
  UpdateColumnInput,
  CreateCardInput,
  UpdateCardInput,
  MoveCardInput,
  BoardSummary,
} from '@/services/types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class ApiClient implements KanbanService {
  private token: string | null = null;
  private headers: Record<string, string> = {};

  constructor() {
    // Load token from localStorage on initialization
    const savedToken = localStorage.getItem('auth_token');
    if (savedToken) {
      this.token = savedToken;
      this.headers['Authorization'] = `Bearer ${savedToken}`;
    }
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...this.headers,
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  // Auth methods
  async register(input: RegisterInput): Promise<{ user: User; token: string }> {
    const result = await this.request<{ user: User; token: string }>(
      '/auth/register',
      {
        method: 'POST',
        body: JSON.stringify(input),
      }
    );
    
    this.setToken(result.token);
    return result;
  }

  async login(input: LoginInput): Promise<{ user: User; token: string }> {
    const result = await this.request<{ user: User; token: string }>(
      '/auth/login',
      {
        method: 'POST',
        body: JSON.stringify(input),
      }
    );
    
    this.setToken(result.token);
    return result;
  }

  async logout(): Promise<void> {
    await this.request('/auth/logout', { method: 'POST' });
    this.clearToken();
  }

  async getCurrentUser(): Promise<User | null> {
    try {
      return await this.request<User>('/auth/me');
    } catch {
      this.clearToken();
      return null;
    }
  }

  // Board methods
  async listBoards(): Promise<BoardSummary[]> {
    return await this.request<BoardSummary[]>('/boards');
  }

  async getBoard(boardId: string): Promise<BoardWithDetails> {
    return await this.request<BoardWithDetails>(`/boards/${boardId}`);
  }

  async createBoard(input: CreateBoardInput): Promise<Board> {
    return await this.request<Board>('/boards', {
      method: 'POST',
      body: JSON.stringify(input),
    });
  }

  async updateBoard(boardId: string, input: UpdateBoardInput): Promise<Board> {
    return await this.request<Board>(`/boards/${boardId}`, {
      method: 'PUT',
      body: JSON.stringify(input),
    });
  }

  async deleteBoard(boardId: string): Promise<void> {
    await this.request(`/boards/${boardId}`, { method: 'DELETE' });
  }

  // Column methods
  async createColumn(boardId: string, input: CreateColumnInput): Promise<Column> {
    return await this.request<Column>(`/boards/${boardId}/columns`, {
      method: 'POST',
      body: JSON.stringify(input),
    });
  }

  async updateColumn(
    boardId: string,
    columnId: string,
    input: UpdateColumnInput
  ): Promise<Column> {
    return await this.request<Column>(`/boards/${boardId}/columns/${columnId}`, {
      method: 'PUT',
      body: JSON.stringify(input),
    });
  }

  async deleteColumn(boardId: string, columnId: string): Promise<void> {
    await this.request(`/boards/${boardId}/columns/${columnId}`, { method: 'DELETE' });
  }

  async reorderColumns(boardId: string, columnIds: string[]): Promise<Column[]> {
    return await this.request<Column[]>(`/boards/${boardId}/columns/reorder`, {
      method: 'PUT',
      body: JSON.stringify({ columnIds }),
    });
  }

  // Card methods
  async createCard(boardId: string, input: CreateCardInput): Promise<Card> {
    return await this.request<Card>(`/boards/${boardId}/cards`, {
      method: 'POST',
      body: JSON.stringify(input),
    });
  }

  async updateCard(
    boardId: string,
    cardId: string,
    input: UpdateCardInput
  ): Promise<Card> {
    return await this.request<Card>(`/boards/${boardId}/cards/${cardId}`, {
      method: 'PUT',
      body: JSON.stringify(input),
    });
  }

  async deleteCard(boardId: string, cardId: string): Promise<void> {
    await this.request(`/boards/${boardId}/cards/${cardId}`, { method: 'DELETE' });
  }

  async moveCard(boardId: string, input: MoveCardInput): Promise<Card> {
    return await this.request<Card>(`/boards/${boardId}/cards/move`, {
      method: 'PUT',
      body: JSON.stringify({ 
        cardId: input.cardId,
        targetColumnId: input.targetColumnId 
      }),
    });
  }

  // Participant methods
  async removeParticipant(boardId: string, userId: string): Promise<void> {
    await this.request(`/boards/${boardId}/participants/${userId}`, { method: 'DELETE' });
  }

  async leaveBoard(boardId: string): Promise<void> {
    await this.request(`/boards/${boardId}/participants/me`, { method: 'DELETE' });
  }

  // Invitation methods
  async createInvitation(boardId: string): Promise<Invitation> {
    return await this.request<Invitation>(`/boards/${boardId}/invitations`, {
      method: 'POST',
    });
  }

  async listInvitations(boardId: string): Promise<Invitation[]> {
    return await this.request<Invitation[]>(`/boards/${boardId}/invitations`);
  }

  async getInvitationByToken(token: string): Promise<Invitation | null> {
    try {
      return await this.request<Invitation>(`/invitations/${token}`);
    } catch {
      return null;
    }
  }

  // Search methods
  async searchCards(boardId: string, query: string): Promise<Card[]> {
    return await this.request<Card[]>(`/boards/${boardId}/search?q=${encodeURIComponent(query)}`);
  }

  async filterCardsByAssignee(boardId: string, assigneeId: string | null): Promise<Card[]> {
    const param = assigneeId ? `?assigneeId=${assigneeId}` : '';
    return await this.request<Card[]>(`/boards/${boardId}/cards${param}`);
  }

  // Token management
  private setToken(token: string): void {
    this.token = token;
    this.headers['Authorization'] = `Bearer ${token}`;
    localStorage.setItem('auth_token', token);
  }

  private clearToken(): void {
    this.token = null;
    delete this.headers['Authorization'];
    localStorage.removeItem('auth_token');
  }
}

// Export singleton instance
export const apiService = new ApiClient();

// Export for direct use if needed
export const service: KanbanService = apiService;