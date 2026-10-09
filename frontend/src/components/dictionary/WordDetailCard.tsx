import React from 'react';
import { Volume2, ExternalLink, Calendar } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Word } from '../../types/word';

interface WordDetailCardProps {
  word: Word;
  showFullLink?: boolean;
}

export const WordDetailCard: React.FC<WordDetailCardProps> = ({
  word,
  showFullLink = true,
}) => {
  const handlePronounce = () => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(word.word);
      utterance.lang = 'en-US';
      utterance.rate = 0.9;
      window.speechSynthesis.speak(utterance);
    }
  };

  const getBadgeClass = (wordType: string | null): string => {
    if (!wordType) return 'badge-default';
    const lower = wordType.toLowerCase();
    if (lower.includes('noun')) return 'badge-noun';
    if (lower.includes('verb')) return 'badge-verb';
    if (lower.includes('adj')) return 'badge-adjective';
    if (lower.includes('adv')) return 'badge-adverb';
    return 'badge-default';
  };

  // Split multiple meanings separated by semicolons
  const meanings = word.meaning
    ? word.meaning
        .split(';')
        .map((m) => m.trim())
        .filter(Boolean)
    : [];

  return (
    <article
      style={{
        backgroundColor: 'var(--color-bg-surface)',
        border: '1px solid var(--color-border)',
        borderRadius: 'var(--radius-xl)',
        boxShadow: 'var(--shadow-md)',
        padding: 'var(--space-6) var(--space-6)',
        width: '100%',
        maxWidth: 'var(--search-box-max)',
        margin: '0 auto',
      }}
      className="animate-fade-in"
    >
      {/* Headword Section */}
      <div
        style={{
          display: 'flex',
          alignItems: 'baseline',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: 'var(--space-2)',
          borderBottom: '1px solid var(--color-border-subtle)',
          paddingBottom: 'var(--space-4)',
          marginBottom: 'var(--space-5)',
        }}
      >
        <div>
          <h2
            className="font-serif"
            style={{
              fontSize: '2.25rem',
              fontWeight: 600,
              color: 'var(--color-text-main)',
              letterSpacing: '-0.02em',
              marginBottom: 'var(--space-1)',
            }}
          >
            {word.word}
          </h2>

          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
            {word.word_type && (
              <span className={`badge ${getBadgeClass(word.word_type)}`}>
                {word.word_type}
              </span>
            )}

            {word.pronunciation && (
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 'var(--space-1)',
                  color: 'var(--color-primary)',
                  fontFamily: 'var(--font-mono)',
                  fontSize: '0.95rem',
                }}
              >
                <span>{word.pronunciation}</span>
                <button
                  type="button"
                  onClick={handlePronounce}
                  title={`Listen to pronunciation of '${word.word}'`}
                  aria-label={`Pronounce '${word.word}'`}
                  style={{
                    padding: '4px',
                    borderRadius: 'var(--radius-full)',
                    color: 'var(--color-primary)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                  className="audio-btn"
                >
                  <Volume2 size={16} />
                </button>
              </div>
            )}
          </div>
        </div>

        {showFullLink && (
          <Link
            to={`/words/${word.id}`}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px',
              fontSize: '0.8rem',
              color: 'var(--color-text-secondary)',
              padding: 'var(--space-1) var(--space-2)',
              borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--color-border)',
            }}
            className="detail-link"
          >
            <span>Word #{word.id}</span>
            <ExternalLink size={12} />
          </Link>
        )}
      </div>

      {/* Meanings Section */}
      <div style={{ marginBottom: 'var(--space-5)' }}>
        <h3
          style={{
            fontSize: '0.75rem',
            fontWeight: 700,
            textTransform: 'uppercase',
            letterSpacing: '0.06em',
            color: 'var(--color-text-muted)',
            marginBottom: 'var(--space-3)',
          }}
        >
          Vietnamese Definitions
        </h3>

        {meanings.length > 1 ? (
          <ol
            style={{
              paddingLeft: 'var(--space-5)',
              margin: 0,
              display: 'flex',
              flexDirection: 'column',
              gap: 'var(--space-2)',
            }}
          >
            {meanings.map((m, idx) => (
              <li
                key={idx}
                style={{
                  fontSize: '1.05rem',
                  lineHeight: 1.55,
                  color: 'var(--color-text-main)',
                }}
              >
                {m}
              </li>
            ))}
          </ol>
        ) : (
          <p
            style={{
              fontSize: '1.1rem',
              lineHeight: 1.55,
              color: 'var(--color-text-main)',
              margin: 0,
            }}
          >
            {word.meaning}
          </p>
        )}
      </div>

      {/* Example Sentence Section */}
      {word.example && (
        <div
          style={{
            backgroundColor: 'var(--color-bg-subtle)',
            borderLeft: '3px solid var(--color-primary)',
            padding: 'var(--space-3) var(--space-4)',
            borderRadius: '0 var(--radius-md) var(--radius-md) 0',
            marginBottom: 'var(--space-4)',
          }}
        >
          <div
            style={{
              fontSize: '0.7rem',
              fontWeight: 700,
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              color: 'var(--color-text-muted)',
              marginBottom: 'var(--space-1)',
            }}
          >
            Example
          </div>
          <p
            style={{
              fontSize: '0.95rem',
              fontStyle: 'italic',
              color: 'var(--color-text-main)',
              margin: 0,
              lineHeight: 1.5,
            }}
          >
            &ldquo;{word.example}&rdquo;
          </p>
        </div>
      )}

      {/* Metadata Footnote */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          fontSize: '0.75rem',
          color: 'var(--color-text-muted)',
          paddingTop: 'var(--space-3)',
          borderTop: '1px solid var(--color-border-subtle)',
        }}
      >
        <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <Calendar size={12} />
          Updated {new Date(word.updated_at).toLocaleDateString()}
        </span>
        <span style={{ fontFamily: 'var(--font-mono)' }}>Database ID: {word.id}</span>
      </div>

      <style>{`
        .audio-btn:hover {
          background-color: var(--color-primary-light);
        }
        .detail-link:hover {
          border-color: var(--color-primary);
          color: var(--color-primary);
        }
      `}</style>
    </article>
  );
};
