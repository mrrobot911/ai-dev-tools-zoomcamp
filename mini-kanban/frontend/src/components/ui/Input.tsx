import { type InputHTMLAttributes, type TextareaHTMLAttributes } from 'react';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export function Input({ label, error, className = '', id, ...props }: InputProps) {
  return (
    <div className="space-y-1">
      {label && (
        <label htmlFor={id} className="block text-sm font-medium text-slate-700">
          {label}
        </label>
      )}
      <input
        id={id}
        className={`w-full rounded-lg border px-3 py-2 text-sm outline-none transition-colors duration-150 ${
          error
            ? 'border-red-400 focus:border-red-500 focus:ring-1 focus:ring-red-500'
            : 'border-slate-300 focus:border-slate-500 focus:ring-1 focus:ring-slate-500'
        } ${className}`}
        {...props}
      />
      {error && <p className="text-xs text-red-600">{error}</p>}
    </div>
  );
}

interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
}

export function Textarea({ label, error, className = '', id, ...props }: TextareaProps) {
  return (
    <div className="space-y-1">
      {label && (
        <label htmlFor={id} className="block text-sm font-medium text-slate-700">
          {label}
        </label>
      )}
      <textarea
        id={id}
        className={`w-full rounded-lg border px-3 py-2 text-sm outline-none transition-colors duration-150 resize-y ${
          error
            ? 'border-red-400 focus:border-red-500 focus:ring-1 focus:ring-red-500'
            : 'border-slate-300 focus:border-slate-500 focus:ring-1 focus:ring-slate-500'
        } ${className}`}
        {...props}
      />
      {error && <p className="text-xs text-red-600">{error}</p>}
    </div>
  );
}

interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
}

export function Select({ label, error, className = '', id, children, ...props }: SelectProps) {
  return (
    <div className="space-y-1">
      {label && (
        <label htmlFor={id} className="block text-sm font-medium text-slate-700">
          {label}
        </label>
      )}
      <select
        id={id}
        className={`w-full rounded-lg border px-3 py-2 text-sm outline-none transition-colors duration-150 ${
          error
            ? 'border-red-400 focus:border-red-500 focus:ring-1 focus:ring-red-500'
            : 'border-slate-300 focus:border-slate-500 focus:ring-1 focus:ring-slate-500'
        } ${className}`}
        {...props}
      >
        {children}
      </select>
      {error && <p className="text-xs text-red-600">{error}</p>}
    </div>
  );
}
