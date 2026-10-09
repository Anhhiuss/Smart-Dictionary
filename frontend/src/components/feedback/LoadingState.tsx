import React from 'react';
import { Loader2 } from 'lucide-react';

interface LoadingStateProps {
  message?: string;
  size?: 'sm' | 'md' | 'lg';
}

export const LoadingState: React.FC<LoadingStateProps> = ({
  message = 'Loading...',
  size = 'md',
}) => {
  const iconSize = size === 'sm' ? 16 : size === 'lg' ? 32 : 24;

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 'var(--space-8) var(--space-4)',
        color: 'var(--color-text-secondary)',
        gap: 'var(--space-3)',
      }}
      role="status"
      aria-live="polite"
    >
      <Loader2
        size={iconSize}
        style={{
          animation: 'spin 1s linear infinite',
          color: 'var(--color-primary)',
        }}
      />
      <span style={{ fontSize: '0.9rem' }}>{message}</span>
      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};
