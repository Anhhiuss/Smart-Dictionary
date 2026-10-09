import React from 'react';
import { AlertTriangle, Loader2 } from 'lucide-react';
import { Word } from '../../types/word';

interface DeleteWordDialogProps {
  word: Word | null;
  isOpen: boolean;
  isDeleting: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

export const DeleteWordDialog: React.FC<DeleteWordDialogProps> = ({
  word,
  isOpen,
  isDeleting,
  onConfirm,
  onCancel,
}) => {
  if (!isOpen || !word) return null;

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(28, 32, 30, 0.45)',
        backdropFilter: 'blur(2px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 100,
        padding: 'var(--space-4)',
      }}
      role="dialog"
      aria-modal="true"
      aria-labelledby="delete-dialog-title"
    >
      <div
        style={{
          backgroundColor: 'var(--color-bg-surface)',
          borderRadius: 'var(--radius-xl)',
          padding: 'var(--space-6)',
          maxWidth: '460px',
          width: '100%',
          boxShadow: 'var(--shadow-lg)',
          border: '1px solid var(--color-border)',
        }}
        className="animate-fade-in"
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)', marginBottom: 'var(--space-4)' }}>
          <div
            style={{
              padding: '8px',
              borderRadius: 'var(--radius-full)',
              backgroundColor: 'var(--color-error-bg)',
              color: 'var(--color-error)',
            }}
          >
            <AlertTriangle size={24} />
          </div>
          <h3 id="delete-dialog-title" style={{ fontSize: '1.2rem', fontWeight: 600 }}>
            Confirm Deletion
          </h3>
        </div>

        <p style={{ fontSize: '0.95rem', color: 'var(--color-text-secondary)', lineHeight: 1.5, marginBottom: 'var(--space-4)' }}>
          Are you sure you want to permanently delete the entry &ldquo;
          <strong style={{ color: 'var(--color-text-main)' }}>{word.word}</strong>
          &rdquo; (ID: {word.id})?
        </p>

        <p
          style={{
            fontSize: '0.8rem',
            color: 'var(--color-text-muted)',
            backgroundColor: 'var(--color-bg-subtle)',
            padding: 'var(--space-2) var(--space-3)',
            borderRadius: 'var(--radius-md)',
            marginBottom: 'var(--space-6)',
          }}
        >
          Note: This action will delete the entry from SQLite storage and prune its corresponding prefix paths from the in-memory Trie search index.
        </p>

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 'var(--space-3)' }}>
          <button
            type="button"
            onClick={onCancel}
            disabled={isDeleting}
            className="btn btn-secondary"
          >
            Cancel
          </button>

          <button
            type="button"
            onClick={onConfirm}
            disabled={isDeleting}
            className="btn btn-danger"
          >
            {isDeleting && <Loader2 size={16} style={{ animation: 'spin 1s linear infinite' }} />}
            <span>Delete Word</span>
          </button>
        </div>
      </div>
    </div>
  );
};
