/**
 * Query normalization utility matching backend Trie and Levenshtein rules.
 */

export function normalizeQuery(text: string | null | undefined): string {
  if (!text) return '';
  return text.trim().toLowerCase().normalize('NFC');
}
