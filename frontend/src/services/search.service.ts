/**
 * Search and suggestions API service.
 */

import { request } from './api';
import { SearchResult, SuggestionsResponse } from '../types/word';

export const searchService = {
  /**
   * Unified search endpoint distinguishing exact, prefix, and fuzzy matches.
   */
  async search(
    query: string,
    maxDistance = 2,
    limit = 5,
    signal?: AbortSignal
  ): Promise<SearchResult> {
    return request<SearchResult>('/api/search', {
      method: 'GET',
      params: { q: query, max_distance: maxDistance, limit },
      signal,
    });
  },

  /**
   * Real-time prefix autocomplete suggestions from Trie.
   */
  async getSuggestions(
    prefix: string,
    limit = 8,
    signal?: AbortSignal
  ): Promise<SuggestionsResponse> {
    return request<SuggestionsResponse>('/api/suggestions', {
      method: 'GET',
      params: { prefix, limit },
      signal,
    });
  },
};
