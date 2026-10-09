import React, { useState } from 'react';
import { SearchBar } from '../components/search/SearchBar';
import { SearchResultList } from '../components/search/SearchResultList';
import { LoadingState } from '../components/feedback/LoadingState';
import { ErrorState } from '../components/feedback/ErrorState';
import { searchService } from '../services/search.service';
import { SearchResult } from '../types/word';
import { BookOpen, Sparkles, Binary } from 'lucide-react';

export const HomePage: React.FC = () => {
  const [searchResult, setSearchResult] = useState<SearchResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentQuery, setCurrentQuery] = useState('');

  const executeSearch = async (queryText: string) => {
    const trimmed = queryText.trim();
    if (!trimmed) return;

    setCurrentQuery(trimmed);
    setIsLoading(true);
    setError(null);

    try {
      const result = await searchService.search(trimmed, 2, 5);
      setSearchResult(result);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to perform search.';
      setError(msg);
      setSearchResult(null);
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickTagClick = (tag: string) => {
    executeSearch(tag);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-8)' }}>
      {/* Editorial Title & Introduction */}
      <section style={{ textAlign: 'center', maxWidth: '640px', margin: '0 auto', paddingTop: 'var(--space-4)' }}>
        <h1
          className="font-brand"
          style={{
            fontSize: 'clamp(2rem, 5vw, 2.75rem)',
            color: 'var(--color-primary)',
            letterSpacing: '0.04em',
            marginBottom: 'var(--space-2)',
          }}
        >
          Lexi Dictionary
        </h1>
        <p
          style={{
            fontSize: '1.05rem',
            color: 'var(--color-text-secondary)',
            lineHeight: 1.55,
          }}
        >
          English–Vietnamese lexical retrieval powered by an in-memory{' '}
          <strong>Trie</strong> for sub-millisecond prefix matching and manual{' '}
          <strong>Levenshtein Dynamic Programming</strong> for approximate spelling recovery.
        </p>

        {/* Quick Demo Test Queries */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexWrap: 'wrap',
            gap: 'var(--space-2)',
            marginTop: 'var(--space-4)',
            fontSize: '0.8rem',
            color: 'var(--color-text-muted)',
          }}
        >
          <span>Try test queries:</span>
          <button
            type="button"
            onClick={() => handleQuickTagClick('computer')}
            className="quick-tag"
          >
            computer <span style={{ opacity: 0.6 }}>(EN)</span>
          </button>
          <button
            type="button"
            onClick={() => handleQuickTagClick('máy tính')}
            className="quick-tag"
          >
            máy tính <span style={{ opacity: 0.6 }}>(VI)</span>
          </button>
          <button
            type="button"
            onClick={() => handleQuickTagClick('dien thoai')}
            className="quick-tag"
          >
            dien thoai <span style={{ opacity: 0.6 }}>(VI unaccented)</span>
          </button>
          <button
            type="button"
            onClick={() => handleQuickTagClick('comptuer')}
            className="quick-tag"
          >
            comptuer <span style={{ opacity: 0.6 }}>(typo)</span>
          </button>
        </div>
      </section>

      {/* Main Search Input */}
      <section>
        <SearchBar
          initialValue={currentQuery}
          onSearch={executeSearch}
          isLoading={isLoading}
        />
      </section>

      {/* Search Results / Feedback States */}
      <section style={{ minHeight: '280px' }}>
        {isLoading && <LoadingState message="Traversing Trie and computing edit distances..." />}

        {error && (
          <ErrorState
            title="Search Error"
            message={error}
            onRetry={() => executeSearch(currentQuery)}
          />
        )}

        {!isLoading && !error && searchResult && (
          <SearchResultList
            result={searchResult}
            onSelectWord={(word) => executeSearch(word)}
          />
        )}

        {!isLoading && !error && !searchResult && (
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
              gap: 'var(--space-4)',
              maxWidth: '840px',
              margin: 'var(--space-8) auto 0 auto',
            }}
          >
            <div className="feature-card">
              <div className="feature-card-icon">
                <Binary size={20} />
              </div>
              <h4>Trie-Indexed Retrieval</h4>
              <p>
                Headwords are stored in an in-memory prefix tree where exact lookups take O(L) time and autocomplete suggestions scale with prefix length O(P + K).
              </p>
            </div>

            <div className="feature-card">
              <div className="feature-card-icon">
                <Sparkles size={20} />
              </div>
              <h4>Levenshtein Fuzzy Search</h4>
              <p>
                Misspelled queries undergo length-bounded candidate pruning and manual 2D Dynamic Programming distance calculation with multi-tier ranking.
              </p>
            </div>

            <div className="feature-card">
              <div className="feature-card-icon">
                <BookOpen size={20} />
              </div>
              <h4>Dual-Tier Synchronization</h4>
              <p>
                SQLite provides durable relational persistence while transactional service hooks keep in-memory search trees synchronized in real time.
              </p>
            </div>
          </div>
        )}
      </section>

      <style>{`
        .quick-tag {
          padding: 2px 8px;
          border-radius: var(--radius-sm);
          background-color: var(--color-bg-subtle);
          border: 1px solid var(--color-border);
          color: var(--color-text-secondary);
          transition: all var(--transition-fast);
        }
        .quick-tag:hover {
          background-color: var(--color-primary-light);
          color: var(--color-primary);
          border-color: var(--color-primary-border);
        }
        .feature-card {
          padding: var(--space-5);
          background-color: var(--color-bg-surface);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-lg);
          box-shadow: var(--shadow-sm);
        }
        .feature-card-icon {
          width: 36px;
          height: 36px;
          border-radius: var(--radius-md);
          background-color: var(--color-primary-light);
          color: var(--color-primary);
          display: flex;
          align-items: center;
          justify-content: center;
          margin-bottom: var(--space-3);
        }
        .feature-card h4 {
          font-size: 1rem;
          margin-bottom: var(--space-1);
          color: var(--color-text-main);
        }
        .feature-card p {
          font-size: 0.85rem;
          color: var(--color-text-secondary);
          line-height: 1.5;
          margin: 0;
        }
      `}</style>
    </div>
  );
};
