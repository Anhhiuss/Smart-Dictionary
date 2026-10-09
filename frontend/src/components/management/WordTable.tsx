import React from 'react';
import { Edit2, Trash2, ArrowLeft, ArrowRight, BookOpen } from 'lucide-react';
import { Word } from '../../types/word';
import { LoadingState } from '../feedback/LoadingState';
import { EmptyState } from '../feedback/EmptyState';

interface WordTableProps {
  words: Word[];
  isLoading: boolean;
  page: number;
  pageSize: number;
  onPageChange: (newPage: number) => void;
  onEdit: (word: Word) => void;
  onDelete: (word: Word) => void;
}

export const WordTable: React.FC<WordTableProps> = ({
  words,
  isLoading,
  page,
  pageSize,
  onPageChange,
  onEdit,
  onDelete,
}) => {
  const getBadgeClass = (wordType: string | null): string => {
    if (!wordType) return 'badge-default';
    const lower = wordType.toLowerCase();
    if (lower.includes('noun')) return 'badge-noun';
    if (lower.includes('verb')) return 'badge-verb';
    if (lower.includes('adj')) return 'badge-adjective';
    if (lower.includes('adv')) return 'badge-adverb';
    return 'badge-default';
  };

  if (isLoading && words.length === 0) {
    return <LoadingState message="Loading dictionary records..." />;
  }

  if (!isLoading && words.length === 0) {
    return (
      <EmptyState
        title="No entries match your search"
        description="Try adjusting your filter or adding a new word to the dictionary."
        icon={<BookOpen size={24} />}
      />
    );
  }

  return (
    <div style={{ width: '100%' }}>
      {/* Table Container */}
      <div
        style={{
          backgroundColor: 'var(--color-bg-surface)',
          border: '1px solid var(--color-border)',
          borderRadius: 'var(--radius-lg)',
          boxShadow: 'var(--shadow-sm)',
          overflow: 'hidden',
        }}
      >
        <div style={{ overflowX: 'auto' }}>
          <table
            style={{
              width: '100%',
              borderCollapse: 'collapse',
              textAlign: 'left',
              fontSize: '0.9rem',
            }}
          >
            <thead>
              <tr
                style={{
                  backgroundColor: 'var(--color-bg-surface-raised)',
                  borderBottom: '1px solid var(--color-border)',
                  color: 'var(--color-text-secondary)',
                  fontSize: '0.75rem',
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em',
                  fontFamily: 'var(--font-mono)',
                }}
              >
                <th style={{ padding: '12px 16px', width: '70px' }}>ID</th>
                <th style={{ padding: '12px 16px', minWidth: '160px' }}>Word</th>
                <th style={{ padding: '12px 16px', width: '110px' }}>Type</th>
                <th style={{ padding: '12px 16px' }}>Meaning</th>
                <th style={{ padding: '12px 16px', width: '110px', textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {words.map((entry) => (
                <tr
                  key={entry.id}
                  style={{
                    borderBottom: '1px solid var(--color-border-subtle)',
                    transition: 'background-color var(--transition-fast)',
                  }}
                  className="table-row-hover"
                >
                  <td
                    style={{
                      padding: '12px 16px',
                      color: 'var(--color-text-muted)',
                      fontFamily: 'var(--font-mono)',
                      fontSize: '0.8rem',
                    }}
                  >
                    #{entry.id}
                  </td>
                  <td style={{ padding: '12px 16px' }}>
                    <div style={{ display: 'flex', flexDirection: 'column' }}>
                      <span style={{ fontWeight: 600, color: 'var(--color-text-main)', fontSize: '0.95rem' }}>
                        {entry.word}
                      </span>
                      {entry.pronunciation && (
                        <span
                          style={{
                            fontFamily: 'var(--font-mono)',
                            fontSize: '0.75rem',
                            color: 'var(--color-text-muted)',
                          }}
                        >
                          {entry.pronunciation}
                        </span>
                      )}
                    </div>
                  </td>
                  <td style={{ padding: '12px 16px' }}>
                    {entry.word_type ? (
                      <span className={`badge ${getBadgeClass(entry.word_type)}`}>
                        {entry.word_type}
                      </span>
                    ) : (
                      <span style={{ color: 'var(--color-text-muted)', fontSize: '0.8rem' }}>—</span>
                    )}
                  </td>
                  <td
                    style={{
                      padding: '12px 16px',
                      color: 'var(--color-text-secondary)',
                      maxWidth: '340px',
                      whiteSpace: 'nowrap',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                    }}
                    title={entry.meaning}
                  >
                    {entry.meaning}
                  </td>
                  <td style={{ padding: '12px 16px', textAlign: 'right' }}>
                    <div style={{ display: 'inline-flex', gap: 'var(--space-1)' }}>
                      <button
                        type="button"
                        onClick={() => onEdit(entry)}
                        title={`Edit ${entry.word}`}
                        aria-label={`Edit ${entry.word}`}
                        style={{
                          padding: '6px',
                          borderRadius: 'var(--radius-sm)',
                          color: 'var(--color-text-secondary)',
                        }}
                        className="action-btn-hover"
                      >
                        <Edit2 size={16} />
                      </button>
                      <button
                        type="button"
                        onClick={() => onDelete(entry)}
                        title={`Delete ${entry.word}`}
                        aria-label={`Delete ${entry.word}`}
                        style={{
                          padding: '6px',
                          borderRadius: 'var(--radius-sm)',
                          color: 'var(--color-error)',
                        }}
                        className="action-btn-danger-hover"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination Bar */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '12px 16px',
            backgroundColor: 'var(--color-bg-surface-raised)',
            borderTop: '1px solid var(--color-border)',
            fontSize: '0.85rem',
            color: 'var(--color-text-secondary)',
          }}
        >
          <span>Page {page}</span>
          <div style={{ display: 'flex', gap: 'var(--space-2)' }}>
            <button
              type="button"
              onClick={() => onPageChange(page - 1)}
              disabled={page <= 1 || isLoading}
              className="btn btn-secondary"
              style={{ padding: '4px 10px', fontSize: '0.8rem' }}
            >
              <ArrowLeft size={14} /> Previous
            </button>
            <button
              type="button"
              onClick={() => onPageChange(page + 1)}
              disabled={words.length < pageSize || isLoading}
              className="btn btn-secondary"
              style={{ padding: '4px 10px', fontSize: '0.8rem' }}
            >
              Next <ArrowRight size={14} />
            </button>
          </div>
        </div>
      </div>

      <style>{`
        .table-row-hover:hover {
          background-color: var(--color-bg-subtle);
        }
        .action-btn-hover:hover {
          color: var(--color-primary) !important;
          background-color: var(--color-primary-light);
        }
        .action-btn-danger-hover:hover {
          background-color: var(--color-error-bg);
        }
      `}</style>
    </div>
  );
};
