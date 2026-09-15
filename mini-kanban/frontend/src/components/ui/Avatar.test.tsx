import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { Avatar } from '@/components/ui/Avatar';

describe('Avatar', () => {
  it('renders initials from name', () => {
    const { container } = render(<Avatar name="John Doe" />);
    const el = container.firstChild as HTMLElement;
    expect(el.textContent).toBe('JD');
  });

  it('renders single initial for single name', () => {
    const { container } = render(<Avatar name="Alice" />);
    const el = container.firstChild as HTMLElement;
    expect(el.textContent).toBe('A');
  });

  it('renders ? for empty name', () => {
    const { container } = render(<Avatar name="" />);
    const el = container.firstChild as HTMLElement;
    expect(el.textContent).toBe('?');
  });

  it('applies size classes', () => {
    const { container } = render(<Avatar name="Test User" size="lg" />);
    const el = container.firstChild as HTMLElement;
    expect(el.className).toContain('w-12');
  });
});
