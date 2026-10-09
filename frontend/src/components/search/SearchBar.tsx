import React, { useEffect, useRef, useState } from 'react';
import { Search, X, Loader2 } from 'lucide-react';
import { searchService } from '../../services/search.service';
import { SuggestionDropdown } from './SuggestionDropdown';

interface SearchBarProps {
  initialValue?: string;
  onSearch: (query: string) => void;
  isLoading?: boolean;
}

export const SearchBar: React.FC<SearchBarProps> = ({
  initialValue = '',
  onSearch,
  isLoading = false,
}) => {
  const [query, setQuery] = useState(initialValue);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);
  const [isSuggesting, setIsSuggesting] = useState(false);

  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  useEffect(() => {
    setQuery(initialValue);
  }, [initialValue]);

  // Debounced autocomplete effect
  useEffect(() => {
    const trimmed = query.trim();

    // Only request suggestions if query has >= 1 characters
    if (!trimmed) {
      setSuggestions([]);
      setIsDropdownOpen(false);
      setActiveIndex(-1);
      return;
    }

    const timer = setTimeout(async () => {
      // Cancel previous pending suggestion request
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      const controller = new AbortController();
      abortControllerRef.current = controller;

      setIsSuggesting(true);
      try {
        const response = await searchService.getSuggestions(trimmed, 8, controller.signal);
        setSuggestions(response.suggestions);
        setIsDropdownOpen(response.suggestions.length > 0);
        setActiveIndex(-1);
      } catch (err: unknown) {
        if (err instanceof DOMException && err.name === 'AbortError') return;
        setSuggestions([]);
        setIsDropdownOpen(false);
      } finally {
        setIsSuggesting(false);
      }
    }, 220); // 220ms debounce

    return () => {
      clearTimeout(timer);
    };
  }, [query]);

  // Handle outside click to dismiss dropdown
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
        setActiveIndex(-1);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!isDropdownOpen || suggestions.length === 0) {
      if (e.key === 'Enter') {
        e.preventDefault();
        submitSearch(query);
      }
      return;
    }

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setActiveIndex((prev) => (prev < suggestions.length - 1 ? prev + 1 : 0));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setActiveIndex((prev) => (prev > 0 ? prev - 1 : suggestions.length - 1));
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (activeIndex >= 0 && activeIndex < suggestions.length) {
        selectSuggestion(suggestions[activeIndex]);
      } else {
        submitSearch(query);
      }
    } else if (e.key === 'Escape') {
      e.preventDefault();
      setIsDropdownOpen(false);
      setActiveIndex(-1);
    }
  };

  const submitSearch = (searchQuery: string) => {
    const trimmed = searchQuery.trim();
    if (!trimmed) return;
    setIsDropdownOpen(false);
    setActiveIndex(-1);
    onSearch(trimmed);
  };

  const selectSuggestion = (word: string) => {
    setQuery(word);
    setIsDropdownOpen(false);
    setActiveIndex(-1);
    submitSearch(word);
  };

  const handleClear = () => {
    setQuery('');
    setSuggestions([]);
    setIsDropdownOpen(false);
    setActiveIndex(-1);
    inputRef.current?.focus();
  };

  return (
    <div
      ref={containerRef}
      style={{
        position: 'relative',
        width: '100%',
        maxWidth: 'var(--search-box-max)',
        margin: '0 auto',
      }}
    >
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          backgroundColor: 'var(--color-bg-surface)',
          border: '1.5px solid var(--color-border)',
          borderRadius: 'var(--radius-lg)',
          boxShadow: 'var(--shadow-sm)',
          padding: '0 var(--space-4)',
          height: '56px',
          transition: 'all var(--transition-fast)',
        }}
        className="search-input-wrapper"
      >
        <Search
          size={20}
          style={{
            color: 'var(--color-primary)',
            marginRight: 'var(--space-3)',
            flexShrink: 0,
          }}
          aria-hidden="true"
        />

        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => {
            if (suggestions.length > 0) setIsDropdownOpen(true);
          }}
          placeholder="Look up an English word, prefix, or typo (e.g. computer, comp, comptuer)..."
          aria-label="Search English dictionary"
          aria-autocomplete="list"
          aria-controls="search-suggestions-list"
          aria-expanded={isDropdownOpen}
          autoComplete="off"
          spellCheck={false}
          style={{
            flex: 1,
            border: 'none',
            outline: 'none',
            backgroundColor: 'transparent',
            fontSize: '1.05rem',
            color: 'var(--color-text-main)',
            lineHeight: 1.4,
          }}
        />

        {/* Loading Spinner */}
        {(isLoading || isSuggesting) && (
          <Loader2
            size={18}
            style={{
              animation: 'spin 1s linear infinite',
              color: 'var(--color-text-muted)',
              marginLeft: 'var(--space-2)',
            }}
          />
        )}

        {/* Clear Button */}
        {query && (
          <button
            type="button"
            onClick={handleClear}
            aria-label="Clear search input"
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: '28px',
              height: '28px',
              borderRadius: 'var(--radius-full)',
              color: 'var(--color-text-muted)',
              marginLeft: 'var(--space-2)',
              transition: 'all var(--transition-fast)',
            }}
            className="clear-btn"
          >
            <X size={16} />
          </button>
        )}
      </div>

      {/* Autocomplete Dropdown */}
      {isDropdownOpen && (
        <SuggestionDropdown
          suggestions={suggestions}
          activeIndex={activeIndex}
          onSelect={selectSuggestion}
          prefix={query.trim()}
        />
      )}

      <style>{`
        .search-input-wrapper:focus-within {
          border-color: var(--color-primary) !important;
          box-shadow: 0 0 0 3px var(--color-primary-light), var(--shadow-md) !important;
        }
        .clear-btn:hover {
          background-color: var(--color-bg-subtle);
          color: var(--color-text-main) !important;
        }
      `}</style>
    </div>
  );
};
