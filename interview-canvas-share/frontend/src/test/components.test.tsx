import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import CreateSessionPage from '../pages/CreateSessionPage';
import JoinSessionPage from '../pages/JoinSessionPage';
import HomePage from '../pages/HomePage';
import NotesPanel from '../components/NotesPanel';
import DiagramEditor from '../components/DiagramEditor';
import type { Note, DiagramState } from '../types';

describe('HomePage', () => {
  it('renders the title and navigation buttons', () => {
    render(
      <MemoryRouter>
        <HomePage />
      </MemoryRouter>,
    );

    expect(screen.getByText('Conduct collaborative system design interviews')).toBeInTheDocument();
    expect(screen.getByText('Create a Session')).toBeInTheDocument();
    expect(screen.getByText('Join with Code')).toBeInTheDocument();
  });
});

describe('CreateSessionPage', () => {
  it('shows validation error when fields are empty', async () => {
    const user = userEvent.setup();
    render(
      <MemoryRouter>
        <CreateSessionPage />
      </MemoryRouter>,
    );

    const submitButton = screen.getByRole('button', { name: 'Create Session' });
    await user.click(submitButton);

    expect(screen.getByText('Session title and your name are required.')).toBeInTheDocument();
  });

  it('creates a session and navigates on valid input', async () => {
    const user = userEvent.setup();
    render(
      <MemoryRouter>
        <CreateSessionPage />
      </MemoryRouter>,
    );

    await user.type(screen.getByPlaceholderText('e.g. Design a URL shortener'), 'URL Shortener');
    await user.type(screen.getByPlaceholderText('Interviewer name'), 'Alice');
    await user.click(screen.getByRole('button', { name: 'Create Session' }));

    await waitFor(() => {
      expect(screen.queryByText('Creating...')).not.toBeInTheDocument();
    });
  });
});

describe('JoinSessionPage', () => {
  it('shows validation error when fields are empty', async () => {
    const user = userEvent.setup();
    render(
      <MemoryRouter>
        <JoinSessionPage />
      </MemoryRouter>,
    );

    await user.click(screen.getByRole('button', { name: 'Join Session' }));
    expect(screen.getByText('Join code and your name are required.')).toBeInTheDocument();
  });

  it('shows error for invalid join code', async () => {
    const user = userEvent.setup();
    render(
      <MemoryRouter>
        <JoinSessionPage />
      </MemoryRouter>,
    );

    await user.type(screen.getByPlaceholderText('e.g. AB12CD'), 'BADCODE');
    await user.type(screen.getByPlaceholderText('Candidate name'), 'Charlie');
    await user.click(screen.getByRole('button', { name: 'Join Session' }));

    await waitFor(() => {
      expect(screen.getByText('No session found with that join code.')).toBeInTheDocument();
    });
  });
});

describe('NotesPanel', () => {
  const mockNotes: Note[] = [
    {
      id: '1',
      sessionId: 's1',
      authorId: 'p1',
      authorName: 'Alice',
      content: 'Private note',
      visibility: 'private',
      createdAt: 1000,
      updatedAt: 1000,
    },
    {
      id: '2',
      sessionId: 's1',
      authorId: 'p2',
      authorName: 'Bob',
      content: 'Shared note',
      visibility: 'shared',
      createdAt: 2000,
      updatedAt: 2000,
    },
  ];

  it('displays existing notes', () => {
    render(
      <NotesPanel
        notes={mockNotes}
        onAddNote={vi.fn()}
        onUpdateNote={vi.fn()}
        onRemoveNote={vi.fn()}
      />,
    );

    expect(screen.getByText('Private note')).toBeInTheDocument();
    expect(screen.getByText('Shared note')).toBeInTheDocument();
  });

  it('calls onAddNote when adding a note', async () => {
    const user = userEvent.setup();
    const onAddNote = vi.fn();
    render(
      <NotesPanel
        notes={[]}
        onAddNote={onAddNote}
        onUpdateNote={vi.fn()}
        onRemoveNote={vi.fn()}
      />,
    );

    await user.type(screen.getByPlaceholderText('Write a note...'), 'New note content');
    await user.click(screen.getByText('Add'));

    expect(onAddNote).toHaveBeenCalledWith('New note content', 'private');
  });

  it('shows edit and delete buttons for all notes', () => {
    render(
      <NotesPanel
        notes={mockNotes}
        onAddNote={vi.fn()}
        onUpdateNote={vi.fn()}
        onRemoveNote={vi.fn()}
      />,
    );

    // Both notes should have edit/delete buttons now
    const editButtons = screen.getAllByText('Edit');
    const deleteButtons = screen.getAllByText('Delete');
    expect(editButtons).toHaveLength(2);
    expect(deleteButtons).toHaveLength(2);
  });

  it('shows empty state when no notes', () => {
    render(
      <NotesPanel
        notes={[]}
        onAddNote={vi.fn()}
        onUpdateNote={vi.fn()}
        onRemoveNote={vi.fn()}
      />,
    );

    expect(screen.getByText('No notes yet.')).toBeInTheDocument();
  });
});

describe('DiagramEditor', () => {
  it('renders the empty state hint when no elements', () => {
    const state: DiagramState = { elements: [] };
    render(
      <DiagramEditor
        state={state}
        onAddElement={vi.fn()}
        onUpdateElement={vi.fn()}
        onRemoveElement={vi.fn()}
      />,
    );

    expect(screen.getByText('Double-click anywhere to add a box')).toBeInTheDocument();
  });

  it('renders box elements with labels', () => {
    const state: DiagramState = {
      elements: [
        {
          id: '1',
          type: 'box',
          x: 50,
          y: 50,
          width: 140,
          height: 60,
          label: 'API Gateway',
        },
      ],
    };

    const { container } = render(
      <DiagramEditor
        state={state}
        onAddElement={vi.fn()}
        onUpdateElement={vi.fn()}
        onRemoveElement={vi.fn()}
      />,
    );

    const text = container.querySelector('text');
    expect(text?.textContent).toBe('API Gateway');
  });

  it('does not show toolbar when readonly', () => {
    const state: DiagramState = { elements: [] };
    render(
      <DiagramEditor
        state={state}
        onAddElement={vi.fn()}
        onUpdateElement={vi.fn()}
        onRemoveElement={vi.fn()}
        readonly
      />,
    );

    expect(screen.queryByText('+ Box')).not.toBeInTheDocument();
    expect(screen.queryByText('+ Text')).not.toBeInTheDocument();
  });

  it('calls onAddElement when the + Box toolbar button is clicked', async () => {
    const user = userEvent.setup();
    const onAddElement = vi.fn();
    const state: DiagramState = { elements: [] };

    render(
      <DiagramEditor
        state={state}
        onAddElement={onAddElement}
        onUpdateElement={vi.fn()}
        onRemoveElement={vi.fn()}
      />,
    );

    await user.click(screen.getByText('+ Box'));
    expect(onAddElement).toHaveBeenCalledTimes(1);
    const added = onAddElement.mock.calls[0][0];
    expect(added.type).toBe('box');
    expect(added.label).toBe('New Box');
  });
});
