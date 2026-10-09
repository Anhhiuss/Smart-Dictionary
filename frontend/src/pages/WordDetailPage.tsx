import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { ArrowLeft, BookOpen } from 'lucide-react';
import { Word } from '../types/word';
import { wordService } from '../services/word.service';
import { WordDetailCard } from '../components/dictionary/WordDetailCard';
import { LoadingState } from '../components/feedback/LoadingState';
import { ErrorState } from '../components/feedback/ErrorState';

export const WordDetailPage: React.FC = () => {
  const { wordId } = useParams<{ wordId: string }>();
  const navigate = useNavigate();

  const [word, setWord] = useState<Word | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const id = Number(wordId);
    if (!wordId || isNaN(id)) {
      setError(`Invalid dictionary word ID: "${wordId}".`);
      setIsLoading(false);
      return;
    }

    let isMounted = true;
    setIsLoading(true);
    setError(null);

    async function loadWord() {
      try {
        const data = await wordService.getWord(id);
        if (isMounted) {
          setWord(data);
        }
      } catch (err: unknown) {
        if (isMounted) {
          const msg = err instanceof Error ? err.message : 'Word not found.';
          setError(msg);
          setWord(null);
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    loadWord();
    return () => {
      isMounted = false;
    };
  }, [wordId]);

  return (
    <div style={{ maxWidth: 'var(--search-box-max)', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
      {/* Return to Search Action */}
      <nav aria-label="Breadcrumb">
        <button
          type="button"
          onClick={() => navigate(-1)}
          className="btn btn-secondary"
          style={{ fontSize: '0.85rem' }}
        >
          <ArrowLeft size={16} />
          <span>Back to previous view</span>
        </button>
      </nav>

      {/* Content States */}
      {isLoading && <LoadingState message="Fetching word entry from persistent storage..." />}

      {error && (
        <ErrorState
          title="Entry Not Found"
          message={error}
          onRetry={() => window.location.reload()}
        />
      )}

      {!isLoading && !error && word && (
        <WordDetailCard word={word} showFullLink={false} />
      )}

      {/* Useful Return Link */}
      <div style={{ textAlign: 'center', marginTop: 'var(--space-4)' }}>
        <Link
          to="/"
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 'var(--space-2)',
            fontSize: '0.9rem',
            color: 'var(--color-primary)',
            fontWeight: 500,
          }}
        >
          <BookOpen size={16} />
          <span>Search another word in dictionary</span>
        </Link>
      </div>
    </div>
  );
};
