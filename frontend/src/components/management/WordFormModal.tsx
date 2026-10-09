import React, { useEffect, useState } from 'react';
import { X, Loader2, Plus, Edit } from 'lucide-react';
import { Word, WordCreatePayload, WordUpdatePayload } from '../../types/word';

interface WordFormModalProps {
  isOpen: boolean;
  initialWord?: Word | null;
  isSaving: boolean;
  errorMessage?: string | null;
  onClose: () => void;
  onSubmit: (payload: WordCreatePayload | WordUpdatePayload) => Promise<void>;
}

export const WordFormModal: React.FC<WordFormModalProps> = ({
  isOpen,
  initialWord = null,
  isSaving,
  errorMessage = null,
  onClose,
  onSubmit,
}) => {
  const isEditing = Boolean(initialWord);

  const [word, setWord] = useState('');
  const [meaning, setMeaning] = useState('');
  const [pronunciation, setPronunciation] = useState('');
  const [wordType, setWordType] = useState('noun');
  const [example, setExample] = useState('');

  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (initialWord) {
      setWord(initialWord.word);
      setMeaning(initialWord.meaning);
      setPronunciation(initialWord.pronunciation || '');
      setWordType(initialWord.word_type || 'noun');
      setExample(initialWord.example || '');
    } else {
      setWord('');
      setMeaning('');
      setPronunciation('');
      setWordType('noun');
      setExample('');
    }
    setValidationErrors({});
  }, [initialWord, isOpen]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const errors: Record<string, string> = {};
    const trimmedWord = word.trim().toLowerCase();
    const trimmedMeaning = meaning.trim();

    if (!trimmedWord) {
      errors.word = 'Headword is required and cannot be empty.';
    }
    if (!trimmedMeaning) {
      errors.meaning = 'Vietnamese meaning is required.';
    }

    if (Object.keys(errors).length > 0) {
      setValidationErrors(errors);
      return;
    }

    setValidationErrors({});

    const payload: WordCreatePayload = {
      word: trimmedWord,
      meaning: trimmedMeaning,
      pronunciation: pronunciation.trim() || null,
      word_type: wordType.trim().toLowerCase() || null,
      example: example.trim() || null,
    };

    await onSubmit(payload);
  };

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
      aria-labelledby="word-modal-title"
    >
      <div
        style={{
          backgroundColor: 'var(--color-bg-surface)',
          borderRadius: 'var(--radius-xl)',
          padding: 'var(--space-6)',
          maxWidth: '540px',
          width: '100%',
          boxShadow: 'var(--shadow-lg)',
          border: '1px solid var(--color-border)',
          maxHeight: '90vh',
          overflowY: 'auto',
        }}
        className="animate-fade-in"
      >
        {/* Header */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            borderBottom: '1px solid var(--color-border-subtle)',
            paddingBottom: 'var(--space-4)',
            marginBottom: 'var(--space-5)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
            {isEditing ? <Edit size={20} color="var(--color-primary)" /> : <Plus size={20} color="var(--color-primary)" />}
            <h3 id="word-modal-title" style={{ fontSize: '1.25rem', fontWeight: 600 }}>
              {isEditing ? `Edit Entry: ${initialWord?.word}` : 'Add New Dictionary Entry'}
            </h3>
          </div>

          <button
            type="button"
            onClick={onClose}
            disabled={isSaving}
            aria-label="Close dialog"
            style={{
              padding: '4px',
              borderRadius: 'var(--radius-sm)',
              color: 'var(--color-text-muted)',
            }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Global Error Alert (e.g. 409 Conflict) */}
        {errorMessage && (
          <div
            style={{
              padding: 'var(--space-3) var(--space-4)',
              backgroundColor: 'var(--color-error-bg)',
              border: '1px solid var(--color-error-border)',
              borderRadius: 'var(--radius-md)',
              color: 'var(--color-error)',
              fontSize: '0.875rem',
              marginBottom: 'var(--space-4)',
            }}
          >
            {errorMessage}
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
          {/* Headword Field */}
          <div>
            <label
              htmlFor="field-word"
              style={{
                display: 'block',
                fontSize: '0.85rem',
                fontWeight: 600,
                color: 'var(--color-text-main)',
                marginBottom: 'var(--space-1)',
              }}
            >
              Headword (English) <span style={{ color: 'var(--color-error)' }}>*</span>
            </label>
            <input
              id="field-word"
              type="text"
              value={word}
              onChange={(e) => setWord(e.target.value)}
              disabled={isSaving}
              placeholder="e.g. algorithm"
              style={{
                width: '100%',
                padding: 'var(--space-2) var(--space-3)',
                borderRadius: 'var(--radius-md)',
                border: `1px solid ${validationErrors.word ? 'var(--color-error)' : 'var(--color-border)'}`,
                backgroundColor: 'var(--color-bg-surface)',
                fontSize: '0.95rem',
              }}
            />
            {validationErrors.word && (
              <span style={{ fontSize: '0.8rem', color: 'var(--color-error)', marginTop: '2px', display: 'block' }}>
                {validationErrors.word}
              </span>
            )}
          </div>

          {/* Part of Speech & Pronunciation Row */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-3)' }}>
            <div>
              <label
                htmlFor="field-word-type"
                style={{
                  display: 'block',
                  fontSize: '0.85rem',
                  fontWeight: 600,
                  color: 'var(--color-text-main)',
                  marginBottom: 'var(--space-1)',
                }}
              >
                Part of Speech
              </label>
              <select
                id="field-word-type"
                value={wordType}
                onChange={(e) => setWordType(e.target.value)}
                disabled={isSaving}
                style={{
                  width: '100%',
                  padding: 'var(--space-2) var(--space-3)',
                  borderRadius: 'var(--radius-md)',
                  border: '1px solid var(--color-border)',
                  backgroundColor: 'var(--color-bg-surface)',
                  fontSize: '0.95rem',
                }}
              >
                <option value="noun">Noun</option>
                <option value="verb">Verb</option>
                <option value="adjective">Adjective</option>
                <option value="adverb">Adverb</option>
                <option value="preposition">Preposition</option>
                <option value="conjunction">Conjunction</option>
                <option value="pronoun">Pronoun</option>
              </select>
            </div>

            <div>
              <label
                htmlFor="field-pronunciation"
                style={{
                  display: 'block',
                  fontSize: '0.85rem',
                  fontWeight: 600,
                  color: 'var(--color-text-main)',
                  marginBottom: 'var(--space-1)',
                }}
              >
                Pronunciation (IPA)
              </label>
              <input
                id="field-pronunciation"
                type="text"
                value={pronunciation}
                onChange={(e) => setPronunciation(e.target.value)}
                disabled={isSaving}
                placeholder="e.g. /ˈæl.ɡə.rɪ.ðəm/"
                style={{
                  width: '100%',
                  padding: 'var(--space-2) var(--space-3)',
                  borderRadius: 'var(--radius-md)',
                  border: '1px solid var(--color-border)',
                  backgroundColor: 'var(--color-bg-surface)',
                  fontSize: '0.95rem',
                  fontFamily: 'var(--font-mono)',
                }}
              />
            </div>
          </div>

          {/* Meaning Field */}
          <div>
            <label
              htmlFor="field-meaning"
              style={{
                display: 'block',
                fontSize: '0.85rem',
                fontWeight: 600,
                color: 'var(--color-text-main)',
                marginBottom: 'var(--space-1)',
              }}
            >
              Vietnamese Meaning <span style={{ color: 'var(--color-error)' }}>*</span>
            </label>
            <textarea
              id="field-meaning"
              value={meaning}
              onChange={(e) => setMeaning(e.target.value)}
              disabled={isSaving}
              rows={3}
              placeholder="e.g. thuật toán; quy trình tính toán từng bước"
              style={{
                width: '100%',
                padding: 'var(--space-2) var(--space-3)',
                borderRadius: 'var(--radius-md)',
                border: `1px solid ${validationErrors.meaning ? 'var(--color-error)' : 'var(--color-border)'}`,
                backgroundColor: 'var(--color-bg-surface)',
                fontSize: '0.95rem',
                resize: 'vertical',
              }}
            />
            {validationErrors.meaning && (
              <span style={{ fontSize: '0.8rem', color: 'var(--color-error)', marginTop: '2px', display: 'block' }}>
                {validationErrors.meaning}
              </span>
            )}
          </div>

          {/* Example Sentence Field */}
          <div>
            <label
              htmlFor="field-example"
              style={{
                display: 'block',
                fontSize: '0.85rem',
                fontWeight: 600,
                color: 'var(--color-text-main)',
                marginBottom: 'var(--space-1)',
              }}
            >
              Usage Example
            </label>
            <textarea
              id="field-example"
              value={example}
              onChange={(e) => setExample(e.target.value)}
              disabled={isSaving}
              rows={2}
              placeholder="e.g. The algorithm sorts the array in O(n log n) time."
              style={{
                width: '100%',
                padding: 'var(--space-2) var(--space-3)',
                borderRadius: 'var(--radius-md)',
                border: '1px solid var(--color-border)',
                backgroundColor: 'var(--color-bg-surface)',
                fontSize: '0.95rem',
                resize: 'vertical',
              }}
            />
          </div>

          {/* Form Actions */}
          <div
            style={{
              display: 'flex',
              justifyContent: 'flex-end',
              gap: 'var(--space-3)',
              marginTop: 'var(--space-3)',
            }}
          >
            <button
              type="button"
              onClick={onClose}
              disabled={isSaving}
              className="btn btn-secondary"
            >
              Cancel
            </button>

            <button
              type="submit"
              disabled={isSaving}
              className="btn btn-primary"
            >
              {isSaving && <Loader2 size={16} style={{ animation: 'spin 1s linear infinite' }} />}
              <span>{isEditing ? 'Save Changes' : 'Create Entry'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
