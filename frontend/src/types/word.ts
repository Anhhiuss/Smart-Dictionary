/**
 * TypeScript definitions aligning with FastAPI backend schemas.
 */

export interface Word {
  id: number;
  word: string;
  meaning: string;
  pronunciation: string | null;
  word_type: string | null;
  example: string | null;
  created_at: string;
  updated_at: string;
}

export interface WordCreatePayload {
  word: string;
  meaning: string;
  pronunciation?: string | null;
  word_type?: string | null;
  example?: string | null;
}

export interface WordUpdatePayload {
  word?: string;
  meaning?: string;
  pronunciation?: string | null;
  word_type?: string | null;
  example?: string | null;
}

export interface FuzzyCandidate {
  word: string;
  distance: number;
  meaning: string | null;
  pronunciation: string | null;
  word_type: string | null;
}

export type SearchMatchType = 'exact' | 'prefix' | 'fuzzy' | 'none';

export interface SearchResult {
  query: string;
  match_type: SearchMatchType;
  data: Word | null;
  suggestions: string[];
  fuzzy_candidates: FuzzyCandidate[];
}

export interface SuggestionsResponse {
  prefix: string;
  count: number;
  suggestions: string[];
}

export interface HealthResponse {
  status: string;
  database: string;
  trie_indexed_words: number;
  total_db_words: number;
}
