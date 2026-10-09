import React from 'react';
import { Search } from 'lucide-react';

interface SuggestionDropdownProps {
  suggestions: string[];
  activeIndex: number;
  onSelect: (word: string) => void;
  prefix: string;
}

export const SuggestionDropdown: React.FC<SuggestionDropdownProps> = ({
  suggestions,
  activeIndex,
  onSelect,
  prefix,
}) => {
  if (suggestions.length === 0) return null;

  return (
    <ul
      role="listbox"
      id="search-suggestions-list"
      style={{
        position: 'absolute',
        top: 'calc(100% + 4px)',
        left: 0,
        right: 0,
        backgroundColor: 'var(--color-bg-surface)',
        border: '1px solid var(--color-border)',
        borderRadius: 'var(--radius-lg)',
        boxShadow: 'var(--shadow-dropdown)',
        zIndex: 50,
        listStyle: 'none',
        padding: 'var(--space-2) 0',
        margin: 0,
        maxHeight: '320px',
        overflowY: 'auto',
      }}
    >
      <div
        style={{
          padding: '4px 16px 8px 16px',
          fontSize: '0.7rem',
          fontWeight: 600,
          textTransform: 'uppercase',
          letterSpacing: '0.05em',
          color: 'var(--color-text-muted)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          borderBottom: '1px solid var(--color-border-subtle)',
        }}
      >
        <span>Trie Prefix Autocomplete</span>
        <span style={{ fontFamily: 'var(--font-mono)' }}>{suggestions.length} items</span>
      </div>

      {suggestions.map((suggestion, index) => {
        const isSelected = index === activeIndex;

        // Highlight matching prefix portion
        const prefixLower = prefix.toLowerCase();
        const suggestionLower = suggestion.toLowerCase();
        const startsWith = suggestionLower.startsWith(prefixLower);

        return (
          <li
            key={suggestion}
            role="option"
            aria-selected={isSelected}
            onClick={() => onSelect(suggestion)}
            onMouseDown={(e) => e.preventDefault()} // Prevent blur before click
            style={{
              padding: '10px 16px',
              display: 'flex',
              alignItems: 'center',
              gap: 'var(--space-3)',
              cursor: 'pointer',
              backgroundColor: isSelected ? 'var(--color-primary-light)' : 'transparent',
              color: isSelected ? 'var(--color-primary)' : 'var(--color-text-main)',
              fontSize: '0.95rem',
              transition: 'background-color var(--transition-fast)',
            }}
          >
            <Search size={14} style={{ color: isSelected ? 'var(--color-primary)' : 'var(--color-text-muted)' }} />
            <span style={{ flex: 1 }}>
              {startsWith ? (
                <>
                  <strong style={{ color: 'var(--color-primary)', fontWeight: 700 }}>
                    {suggestion.slice(0, prefix.length)}
                  </strong>
                  <span>{suggestion.slice(prefix.length)}</span>
                </>
              ) : (
                suggestion
              )}
            </span>
            <span
              style={{
                fontSize: '0.7rem',
                fontFamily: 'var(--font-mono)',
                color: 'var(--color-text-muted)',
              }}
            >
              Enter ↵
            </span>
          </li>
        );
      })}
    </ul>
  );
};
