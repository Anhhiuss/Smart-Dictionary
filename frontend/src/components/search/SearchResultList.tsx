import React from 'react';
import { Sparkles, ArrowRight, CornerDownRight } from 'lucide-react';
import { SearchResult } from '../../types/word';
import { WordDetailCard } from '../dictionary/WordDetailCard';
import { EmptyState } from '../feedback/EmptyState';

interface SearchResultListProps {
  result: SearchResult;
  onSelectWord: (wordText: string) => void;
}

export const SearchResultList: React.FC<SearchResultListProps> = ({
  result,
  onSelectWord,
}) => {
  const { match_type, query, data, suggestions, fuzzy_candidates } = result;

  // 1. EXACT MATCH
  if (match_type === 'exact' && data) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            maxWidth: 'var(--search-box-max)',
            margin: '0 auto',
            width: '100%',
          }}
        >
          <span className="badge badge-match-exact">
            ✓ Exact Match (Trie O(L))
          </span>
          <span style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>
            Found in {data.word.length} steps
          </span>
        </div>
        <WordDetailCard word={data} />

        {/* Other matching entries (e.g. For Vietnamese queries matching multiple English headwords) */}
        {suggestions.length > 0 && (
          <div
            style={{
              maxWidth: 'var(--search-box-max)',
              margin: '0 auto',
              width: '100%',
              padding: 'var(--space-4)',
              backgroundColor: 'var(--color-bg-surface)',
              border: '1px solid var(--color-border)',
              borderRadius: 'var(--radius-lg)',
            }}
          >
            <span style={{ fontSize: '0.85rem', color: 'var(--color-text-secondary)', display: 'block', marginBottom: 'var(--space-2)' }}>
              Other English translations matching &ldquo;<strong>{query}</strong>&rdquo;:
            </span>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-2)' }}>
              {suggestions.map((w) => (
                <button
                  key={w}
                  type="button"
                  onClick={() => onSelectWord(w)}
                  className="quick-tag"
                  style={{ fontSize: '0.875rem' }}
                >
                  {w} <ArrowRight size={12} style={{ display: 'inline', marginLeft: '4px' }} />
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  }

  // 2. PREFIX MATCHES
  if (match_type === 'prefix' && suggestions.length > 0) {
    return (
      <div
        style={{
          width: '100%',
          maxWidth: 'var(--search-box-max)',
          margin: '0 auto',
          backgroundColor: 'var(--color-bg-surface)',
          border: '1px solid var(--color-border)',
          borderRadius: 'var(--radius-xl)',
          padding: 'var(--space-6)',
          boxShadow: 'var(--shadow-sm)',
        }}
        className="animate-fade-in"
      >
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: 'var(--space-4)',
            borderBottom: '1px solid var(--color-border-subtle)',
            paddingBottom: 'var(--space-3)',
          }}
        >
          <div>
            <span className="badge badge-match-prefix">
              Prefix Matches (Trie Subtree)
            </span>
            <p
              style={{
                fontSize: '0.875rem',
                color: 'var(--color-text-secondary)',
                marginTop: 'var(--space-1)',
              }}
            >
              No exact match for &ldquo;<strong>{query}</strong>&rdquo;, but found words beginning with this prefix:
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
          {suggestions.map((word) => (
            <button
              key={word}
              type="button"
              onClick={() => onSelectWord(word)}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: 'var(--space-3) var(--space-4)',
                backgroundColor: 'var(--color-bg-surface-raised)',
                border: '1px solid var(--color-border-subtle)',
                borderRadius: 'var(--radius-md)',
                textAlign: 'left',
                transition: 'all var(--transition-fast)',
              }}
              className="prefix-result-item"
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
                <CornerDownRight size={16} style={{ color: 'var(--color-primary)' }} />
                <span style={{ fontSize: '1.05rem', fontWeight: 600, color: 'var(--color-text-main)' }}>
                  {word}
                </span>
              </div>
              <span
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                  fontSize: '0.8rem',
                  color: 'var(--color-primary)',
                  fontWeight: 500,
                }}
              >
                View definition <ArrowRight size={14} />
              </span>
            </button>
          ))}
        </div>

        <style>{`
          .prefix-result-item:hover {
            border-color: var(--color-primary-border);
            background-color: var(--color-primary-light);
            transform: translateX(2px);
          }
        `}</style>
      </div>
    );
  }

  // 3. FUZZY MATCHES (LEVENSHTEIN APPROXIMATE SEARCH)
  if (match_type === 'fuzzy' && fuzzy_candidates.length > 0) {
    return (
      <div
        style={{
          width: '100%',
          maxWidth: 'var(--search-box-max)',
          margin: '0 auto',
          backgroundColor: 'var(--color-bg-surface)',
          border: '1px solid var(--color-fuzzy-border)',
          borderRadius: 'var(--radius-xl)',
          padding: 'var(--space-6)',
          boxShadow: 'var(--shadow-sm)',
        }}
        className="animate-fade-in"
      >
        <div
          style={{
            display: 'flex',
            alignItems: 'flex-start',
            gap: 'var(--space-3)',
            marginBottom: 'var(--space-4)',
            borderBottom: '1px solid var(--color-border-subtle)',
            paddingBottom: 'var(--space-4)',
          }}
        >
          <div
            style={{
              padding: '8px',
              borderRadius: 'var(--radius-md)',
              backgroundColor: 'var(--color-fuzzy-bg)',
              color: 'var(--color-fuzzy)',
            }}
          >
            <Sparkles size={20} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
              <span className="badge badge-match-fuzzy">
                Did You Mean? (Levenshtein DP)
              </span>
            </div>
            <p
              style={{
                fontSize: '0.9rem',
                color: 'var(--color-text-secondary)',
                marginTop: 'var(--space-1)',
              }}
            >
              No exact or prefix match found for &ldquo;<strong>{query}</strong>&rdquo;. Showing ranked approximate corrections:
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
          {fuzzy_candidates.map((candidate) => (
            <button
              key={candidate.word}
              type="button"
              onClick={() => onSelectWord(candidate.word)}
              style={{
                display: 'flex',
                flexDirection: 'column',
                gap: '4px',
                padding: 'var(--space-3) var(--space-4)',
                backgroundColor: 'var(--color-bg-app)',
                border: '1px solid var(--color-border)',
                borderRadius: 'var(--radius-md)',
                textAlign: 'left',
                transition: 'all var(--transition-fast)',
              }}
              className="fuzzy-result-item"
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
                  <span style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--color-primary)' }}>
                    {candidate.word}
                  </span>
                  {candidate.word_type && (
                    <span className="badge badge-default" style={{ fontSize: '0.65rem' }}>
                      {candidate.word_type}
                    </span>
                  )}
                  {candidate.pronunciation && (
                    <span
                      style={{
                        fontFamily: 'var(--font-mono)',
                        fontSize: '0.8rem',
                        color: 'var(--color-text-muted)',
                      }}
                    >
                      {candidate.pronunciation}
                    </span>
                  )}
                </div>

                <span
                  style={{
                    fontFamily: 'var(--font-mono)',
                    fontSize: '0.75rem',
                    padding: '2px 8px',
                    borderRadius: 'var(--radius-sm)',
                    backgroundColor: 'var(--color-fuzzy-bg)',
                    color: 'var(--color-fuzzy)',
                    fontWeight: 600,
                  }}
                >
                  Edit distance: {candidate.distance}
                </span>
              </div>

              {candidate.meaning && (
                <p
                  style={{
                    fontSize: '0.875rem',
                    color: 'var(--color-text-secondary)',
                    margin: 0,
                    lineHeight: 1.4,
                  }}
                >
                  {candidate.meaning}
                </p>
              )}
            </button>
          ))}
        </div>

        <style>{`
          .fuzzy-result-item:hover {
            border-color: var(--color-primary);
            background-color: var(--color-bg-surface);
            box-shadow: var(--shadow-sm);
          }
        `}</style>
      </div>
    );
  }

  // 4. NO MATCH
  return (
    <EmptyState
      title={`No matches found for "${query}"`}
      description="Neither exact, prefix, nor close approximate matches (within edit distance 2) were found in the dictionary."
    />
  );
};
