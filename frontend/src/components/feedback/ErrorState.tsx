import React from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';

interface ErrorStateProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title = 'Something went wrong',
  message = 'An unexpected error occurred while communicating with the server.',
  onRetry,
}) => {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 'var(--space-8) var(--space-4)',
        textAlign: 'center',
        backgroundColor: 'var(--color-error-bg)',
        border: '1px solid var(--color-error-border)',
        borderRadius: 'var(--radius-lg)',
        maxWidth: '540px',
        margin: 'var(--space-6) auto',
      }}
      role="alert"
    >
      <AlertCircle
        size={32}
        style={{ color: 'var(--color-error)', marginBottom: 'var(--space-3)' }}
      />
      <h4
        style={{
          fontSize: '1rem',
          fontWeight: 600,
          color: 'var(--color-error)',
          marginBottom: 'var(--space-1)',
        }}
      >
        {title}
      </h4>
      <p
        style={{
          fontSize: '0.875rem',
          color: 'var(--color-text-secondary)',
          lineHeight: 1.5,
          marginBottom: onRetry ? 'var(--space-4)' : 0,
        }}
      >
        {message}
      </p>
      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="btn btn-secondary"
          style={{ fontSize: '0.8rem', padding: 'var(--space-1) var(--space-3)' }}
        >
          <RefreshCw size={14} />
          Retry
        </button>
      )}
    </div>
  );
};
