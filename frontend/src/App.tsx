import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Header } from './components/layout/Header';
import { HomePage } from './pages/HomePage';
import { WordDetailPage } from './pages/WordDetailPage';
import { ManagementPage } from './pages/ManagementPage';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <div className="app-container">
        <Header />

        <main className="main-content">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/words/:wordId" element={<WordDetailPage />} />
            <Route path="/manage" element={<ManagementPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>

        <footer
          style={{
            borderTop: '1px solid var(--color-border)',
            backgroundColor: 'var(--color-bg-surface)',
            padding: 'var(--space-6) var(--space-4)',
            textAlign: 'center',
            fontSize: '0.8rem',
            color: 'var(--color-text-muted)',
            marginTop: 'auto',
          }}
        >
          <div style={{ maxWidth: 'var(--container-max)', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <p>
              <strong>Smart Dictionary (Lexi)</strong> &mdash; University Data Structures and Algorithms Project
            </p>
            <p>
              In-Memory Trie &bull; Manual Dynamic Programming Levenshtein Distance &bull; SQLite Relational Persistence
            </p>
          </div>
        </footer>
      </div>
    </BrowserRouter>
  );
};

export default App;
