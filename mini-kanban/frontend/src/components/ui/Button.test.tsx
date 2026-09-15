import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Button } from '@/components/ui/Button';
import { Trash2 } from 'lucide-react';

describe('Button', () => {
  it('renders children', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole('button', { name: /click me/i })).toBeDefined();
  });

  it('applies variant classes', () => {
    render(<Button variant="danger">Delete</Button>);
    const btn = screen.getByRole('button');
    expect(btn.className).toContain('bg-red-600');
  });

  it('applies size classes', () => {
    render(<Button size="lg">Large</Button>);
    const btn = screen.getByRole('button');
    expect(btn.className).toContain('px-6');
  });

  it('is disabled when disabled prop is set', () => {
    render(<Button disabled>Disabled</Button>);
    expect(screen.getByRole('button').hasAttribute('disabled')).toBe(true);
  });

  it('renders with icon', () => {
    render(
      <Button>
        <Trash2 size={16} />
        Delete
      </Button>
    );
    expect(screen.getByRole('button', { name: /delete/i })).toBeDefined();
  });
});
