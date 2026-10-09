/**
 * Word dictionary CRUD and health inspection service.
 */

import { request } from './api';
import {
  HealthResponse,
  Word,
  WordCreatePayload,
  WordUpdatePayload,
} from '../types/word';

export const wordService = {
  /**
   * List paginated words with optional substring search.
   */
  async listWords(
    skip = 0,
    limit = 50,
    search?: string,
    signal?: AbortSignal
  ): Promise<Word[]> {
    return request<Word[]>('/api/words', {
      method: 'GET',
      params: { skip, limit, search },
      signal,
    });
  },

  /**
   * Get word detail by ID.
   */
  async getWord(id: number, signal?: AbortSignal): Promise<Word> {
    return request<Word>(`/api/words/${id}`, {
      method: 'GET',
      signal,
    });
  },

  /**
   * Create a new dictionary entry.
   */
  async createWord(payload: WordCreatePayload): Promise<Word> {
    return request<Word>('/api/words', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  /**
   * Update an existing dictionary entry.
   */
  async updateWord(id: number, payload: WordUpdatePayload): Promise<Word> {
    return request<Word>(`/api/words/${id}`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    });
  },

  /**
   * Delete an existing dictionary entry.
   */
  async deleteWord(id: number): Promise<{ success: boolean; message: string }> {
    return request<{ success: boolean; message: string }>(`/api/words/${id}`, {
      method: 'DELETE',
    });
  },

  /**
   * Fetch system health status, DB connectivity, and Trie index count.
   */
  async getHealth(signal?: AbortSignal): Promise<HealthResponse> {
    return request<HealthResponse>('/api/health', {
      method: 'GET',
      signal,
    });
  },
};
