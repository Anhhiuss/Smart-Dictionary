import React, { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { BookMarked, Database } from 'lucide-react';
import { wordService } from '../../services/word.service';

export const Header: React.FC = () => {
  const location = useLocation();
  const [indexCount, setIndexCount] = useState<number | null>(null);
  const [isOnline, setIsOnline] = useState<boolean>(true);

  useEffect(() => {
    let isMounted = true;

    async function checkHealth() {
      try {
        const health = await wordService.getHealth();
        if (isMounted) {
          setIsOnline(health.status === 'healthy');
          setIndexCount(health.trie_indexed_words);
        }
      } catch {
        if (isMounted) {
          setIsOnline(false);
        }
      }
    }

    checkHealth();
    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <header className="site-header">
      <div className="header-inner">
        <Link to="/" className="brand-link" aria-label="Lexi Dictionary Home">
          <BookMarked size={24} style={{ color: 'var(--color-primary)' }} />
          <span>LEXI</span>
          <span className="brand-badge">TRIE &amp; DP</span>
        </Link>

        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-4)' }}>
          {/* Index Counter Status Indicator */}
          <div
            style={{
              display: 'none',
              alignItems: 'center',
              gap: '6px',
              fontSize: '0.75rem',
              color: 'var(--color-text-muted)',
              fontFamily: 'var(--font-mono)',
            }}
            className="header-status"
          >
            <span
              style={{
                width: '7px',
                height: '7px',
                borderRadius: '50%',
                backgroundColor: isOnline ? '#22c55e' : '#ef4444',
                display: 'inline-block',
              }}
            />
            <span>
              {isOnline
                ? indexCount !== null
                  ? `${indexCount.toLocaleString()} words indexed`
                  : 'Connected'
                : 'Offline'}
            </span>
          </div>

          {/* Navigation Links */}
          <nav className="site-nav" aria-label="Main Navigation">
            <Link
              to="/"
              className={`nav-link ${location.pathname === '/' || location.pathname.startsWith('/words/') ? 'active' : ''}`}
            >
              <BookMarked size={16} />
              <span>Dictionary</span>
            </Link>
            <Link
              to="/manage"
              className={`nav-link ${location.pathname === '/manage' ? 'active' : ''}`}
            >
              <Database size={16} />
              <span>Manage</span>
            </Link>
          </nav>
        </div>
      </div>

      <style>{`
        @media (min-width: 640px) {
          .header-status {
            display: flex !important;
          }
        }
      `}</style>
    </header>
  );
};
