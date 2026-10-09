import React from 'react';
import { BookOpen } from 'lucide-react';

interface EmptyStateProps {
  title?: string;
  description?: string;
  action?: React.ReactNode;
  icon?: React.ReactNode;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title = 'No results found',
  description = 'Try searching with a different spelling or prefix.',
  action,
  icon,
}) => {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 'var(--space-12) var(--space-4)',
        textAlign: 'center',
        backgroundColor: 'var(--color-bg-surface)',
        borderRadius: 'var(--radius-lg)',
        border: '1px dashed var(--color-border)',
        maxWidth: '540px',
        margin: '0 auto',
      }}
    >
      <div
        style={{
          width: '48px',
          height: '48px',
          borderRadius: 'var(--radius-full)',
          backgroundColor: 'var(--color-bg-subtle)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'var(--color-text-muted)',
          marginBottom: 'var(--space-4)',
        }}
      >
        {icon || <BookOpen size={24} />}
      </div>
      <h3
        style={{
          fontSize: '1.1rem',
          fontWeight: 600,
          marginBottom: 'var(--space-2)',
          color: 'var(--color-text-main)',
        }}
      >
        {title}
      </h3>
      <p
        style={{
          fontSize: '0.9rem',
          color: 'var(--color-text-secondary)',
          lineHeight: 1.5,
          marginBottom: action ? 'var(--space-6)' : 0,
        }}
      >
        {description}
      </p>
      {action && <div>{action}</div>}
    </div>
  );
};
