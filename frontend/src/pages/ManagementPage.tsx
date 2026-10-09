import React, { useEffect, useState, useCallback } from 'react';
import { Plus, Search, RefreshCw, CheckCircle2, AlertCircle } from 'lucide-react';
import { Word, WordCreatePayload, WordUpdatePayload } from '../types/word';
import { wordService } from '../services/word.service';
import { WordTable } from '../components/management/WordTable';
import { WordFormModal } from '../components/management/WordFormModal';
import { DeleteWordDialog } from '../components/management/DeleteWordDialog';
import { useDebounce } from '../hooks/useDebounce';
import { ErrorState } from '../components/feedback/ErrorState';

export const ManagementPage: React.FC = () => {
  const [words, setWords] = useState<Word[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Pagination & Search
  const [page, setPage] = useState(1);
  const pageSize = 25;
  const [searchFilter, setSearchFilter] = useState('');
  const debouncedFilter = useDebounce(searchFilter, 300);

  // Modal & Dialog States
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingWord, setEditingWord] = useState<Word | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const [deletingWord, setDeletingWord] = useState<Word | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  // Toast Notification
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

  const showToast = (message: string, type: 'success' | 'error' = 'success') => {
    setToast({ message, type });
    setTimeout(() => {
      setToast(null);
    }, 4000);
  };

  const loadWords = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const skip = (page - 1) * pageSize;
      const data = await wordService.listWords(skip, pageSize, debouncedFilter.trim() || undefined);
      setWords(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to load dictionary records.';
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  }, [page, pageSize, debouncedFilter]);

  useEffect(() => {
    loadWords();
  }, [loadWords]);

  // When search filter changes, reset to page 1
  useEffect(() => {
    setPage(1);
  }, [debouncedFilter]);

  const handleCreateNew = () => {
    setEditingWord(null);
    setFormError(null);
    setIsFormOpen(true);
  };

  const handleEdit = (word: Word) => {
    setEditingWord(word);
    setFormError(null);
    setIsFormOpen(true);
  };

  const handleFormSubmit = async (payload: WordCreatePayload | WordUpdatePayload) => {
    setIsSaving(true);
    setFormError(null);

    try {
      if (editingWord) {
        // Edit existing word
        const updated = await wordService.updateWord(editingWord.id, payload);
        showToast(`Successfully updated entry "${updated.word}".`);
      } else {
        // Create new word
        const created = await wordService.createWord(payload as WordCreatePayload);
        showToast(`Successfully created entry "${created.word}".`);
      }
      setIsFormOpen(false);
      setEditingWord(null);
      await loadWords();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Operation failed.';
      setFormError(msg);
    } finally {
      setIsSaving(false);
    }
  };

  const handleDeleteTrigger = (word: Word) => {
    setDeletingWord(word);
  };

  const handleConfirmDelete = async () => {
    if (!deletingWord) return;

    setIsDeleting(true);
    try {
      await wordService.deleteWord(deletingWord.id);
      showToast(`Deleted entry "${deletingWord.word}" from SQLite and pruned from Trie.`);
      setDeletingWord(null);
      await loadWords();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to delete word.';
      showToast(msg, 'error');
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
      {/* Toast Notification Banner */}
      {toast && (
        <div
          style={{
            position: 'fixed',
            bottom: '24px',
            right: '24px',
            backgroundColor: toast.type === 'success' ? 'var(--color-primary)' : 'var(--color-error)',
            color: '#ffffff',
            padding: '12px 20px',
            borderRadius: 'var(--radius-lg)',
            boxShadow: 'var(--shadow-lg)',
            display: 'flex',
            alignItems: 'center',
            gap: 'var(--space-3)',
            zIndex: 110,
            fontSize: '0.9rem',
            fontWeight: 500,
          }}
          className="animate-fade-in"
        >
          {toast.type === 'success' ? <CheckCircle2 size={18} /> : <AlertCircle size={18} />}
          <span>{toast.message}</span>
        </div>
      )}

      {/* Page Header */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: 'var(--space-4)',
          borderBottom: '1px solid var(--color-border)',
          paddingBottom: 'var(--space-4)',
        }}
      >
        <div>
          <h2 style={{ fontSize: '1.75rem', fontWeight: 600, color: 'var(--color-text-main)' }}>
            Dictionary Management
          </h2>
          <p style={{ fontSize: '0.9rem', color: 'var(--color-text-secondary)', marginTop: '2px' }}>
            Inspect, filter, add, edit, and delete entries synchronized in real time with the Trie index.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
          <button
            type="button"
            onClick={loadWords}
            disabled={isLoading}
            className="btn btn-secondary"
            title="Refresh dictionary list"
          >
            <RefreshCw size={15} style={{ animation: isLoading ? 'spin 1s linear infinite' : 'none' }} />
            <span>Refresh</span>
          </button>

          <button
            type="button"
            onClick={handleCreateNew}
            className="btn btn-primary"
          >
            <Plus size={16} />
            <span>Add New Word</span>
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          backgroundColor: 'var(--color-bg-surface)',
          border: '1px solid var(--color-border)',
          borderRadius: 'var(--radius-md)',
          padding: '0 var(--space-3)',
          maxWidth: '420px',
          height: '42px',
        }}
      >
        <Search size={16} style={{ color: 'var(--color-text-muted)', marginRight: 'var(--space-2)' }} />
        <input
          type="text"
          value={searchFilter}
          onChange={(e) => setSearchFilter(e.target.value)}
          placeholder="Filter words by substring (e.g. comp)..."
          style={{
            border: 'none',
            outline: 'none',
            backgroundColor: 'transparent',
            width: '100%',
            fontSize: '0.9rem',
          }}
        />
        {searchFilter && (
          <button
            type="button"
            onClick={() => setSearchFilter('')}
            style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}
          >
            Clear
          </button>
        )}
      </div>

      {/* Error State */}
      {error && (
        <ErrorState
          title="Could not load entries"
          message={error}
          onRetry={loadWords}
        />
      )}

      {/* Table Component */}
      {!error && (
        <WordTable
          words={words}
          isLoading={isLoading}
          page={page}
          pageSize={pageSize}
          onPageChange={(p) => setPage(p)}
          onEdit={handleEdit}
          onDelete={handleDeleteTrigger}
        />
      )}

      {/* Modals */}
      <WordFormModal
        isOpen={isFormOpen}
        initialWord={editingWord}
        isSaving={isSaving}
        errorMessage={formError}
        onClose={() => setIsFormOpen(false)}
        onSubmit={handleFormSubmit}
      />

      <DeleteWordDialog
        isOpen={Boolean(deletingWord)}
        word={deletingWord}
        isDeleting={isDeleting}
        onConfirm={handleConfirmDelete}
        onCancel={() => setDeletingWord(null)}
      />
    </div>
  );
};
