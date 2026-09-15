import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Modal } from '@/components/ui/Modal';

describe('Modal', () => {
  it('renders when open', () => {
    render(
      <Modal open={true} onClose={() => {}} title="Test Modal">
        <p>Modal content</p>
      </Modal>
    );
    expect(screen.getByText('Test Modal')).toBeDefined();
    expect(screen.getByText('Modal content')).toBeDefined();
  });

  it('does not render when closed', () => {
    render(
      <Modal open={false} onClose={() => {}} title="Test Modal">
        <p>Modal content</p>
      </Modal>
    );
    expect(screen.queryByText('Test Modal')).toBeNull();
  });

  it('calls onClose when close button clicked', async () => {
    const onClose = vi.fn();
    render(
      <Modal open={true} onClose={onClose} title="Test Modal">
        <p>Content</p>
      </Modal>
    );
    await userEvent.click(screen.getByRole('button', { name: '' }));
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('calls onClose when Escape is pressed', async () => {
    const onClose = vi.fn();
    render(
      <Modal open={true} onClose={onClose} title="Test Modal">
        <p>Content</p>
      </Modal>
    );
    await userEvent.keyboard('{Escape}');
    expect(onClose).toHaveBeenCalledTimes(1);
  });
});
