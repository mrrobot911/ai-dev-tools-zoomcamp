import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { CardModal } from '@/components/board/CardModal';
import type { Card, Participant } from '@/types';

const mockParticipants: Participant[] = [
  { userId: 'u1', email: 'alice@example.com', name: 'Alice', role: 'owner', joinedAt: '2024-01-01' },
  { userId: 'u2', email: 'bob@example.com', name: 'Bob', role: 'participant', joinedAt: '2024-01-01' },
];

const mockCard: Card = {
  id: 'card1',
  boardId: 'board1',
  columnId: 'col1',
  title: 'Test Card',
  description: 'Test description',
  creatorId: 'u1',
  creatorName: 'Alice',
  assigneeId: 'u1',
  assigneeName: 'Alice',
  createdAt: '2024-01-01T00:00:00Z',
  updatedAt: '2024-01-01T00:00:00Z',
};

describe('CardModal', () => {
  it('renders with card data when editing', () => {
    render(
      <CardModal
        open={true}
        onClose={() => {}}
        card={mockCard}
        columnId="col1"
        participants={mockParticipants}
        onSave={vi.fn()}
        canDelete={false}
      />
    );
    expect(screen.getByDisplayValue('Test Card')).toBeDefined();
    expect(screen.getByDisplayValue('Test description')).toBeDefined();
  });

  it('renders empty form for new card', () => {
    render(
      <CardModal
        open={true}
        onClose={() => {}}
        card={null}
        columnId="col1"
        participants={mockParticipants}
        onSave={vi.fn()}
        canDelete={false}
      />
    );
    expect(screen.getByText('New card')).toBeDefined();
    expect(screen.getByPlaceholderText('Card title')).toBeDefined();
  });

  it('shows participants in assignee dropdown', () => {
    render(
      <CardModal
        open={true}
        onClose={() => {}}
        card={null}
        columnId="col1"
        participants={mockParticipants}
        onSave={vi.fn()}
        canDelete={false}
      />
    );
    expect(screen.getByText('Alice (Owner)')).toBeDefined();
    expect(screen.getByText('Bob')).toBeDefined();
  });

  it('calls onSave with form data', async () => {
    const onSave = vi.fn().mockResolvedValue(undefined);
    render(
      <CardModal
        open={true}
        onClose={() => {}}
        card={null}
        columnId="col1"
        participants={mockParticipants}
        onSave={onSave}
        canDelete={false}
      />
    );
    await userEvent.type(screen.getByPlaceholderText('Card title'), 'New Task');
    await userEvent.click(screen.getByText('Create card'));
    await waitFor(() => {
      expect(onSave).toHaveBeenCalledWith({
        title: 'New Task',
        description: '',
        assigneeId: null,
      });
    });
  });

  it('shows delete button only when canDelete is true', () => {
    const { rerender } = render(
      <CardModal
        open={true}
        onClose={() => {}}
        card={mockCard}
        columnId="col1"
        participants={mockParticipants}
        onSave={vi.fn()}
        onDelete={vi.fn().mockResolvedValue(undefined)}
        canDelete={true}
      />
    );
    expect(screen.getByText('Delete')).toBeDefined();

    rerender(
      <CardModal
        open={true}
        onClose={() => {}}
        card={mockCard}
        columnId="col1"
        participants={mockParticipants}
        onSave={vi.fn()}
        canDelete={false}
      />
    );
    expect(screen.queryByText('Delete')).toBeNull();
  });

  it('shows creator and timestamps when editing', () => {
    render(
      <CardModal
        open={true}
        onClose={() => {}}
        card={mockCard}
        columnId="col1"
        participants={mockParticipants}
        onSave={vi.fn()}
        canDelete={false}
      />
    );
    expect(screen.getByText('Created by Alice')).toBeDefined();
  });
});
