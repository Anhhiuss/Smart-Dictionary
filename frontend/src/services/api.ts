/**
 * Centralized API HTTP client with error extraction and environment configuration.
 */

const BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000').replace(/\/+$/, '');

export class ApiError extends Error {
  status: number;
  data: unknown;

  constructor(message: string, status: number, data?: unknown) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

interface RequestOptions extends RequestInit {
  params?: Record<string, string | number | boolean | undefined | null>;
}

export async function request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
  const { params, headers, ...restOptions } = options;

  let url = `${BASE_URL}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;

  if (params) {
    const searchParams = new URLSearchParams();
    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined && value !== null && value !== '') {
        searchParams.append(key, String(value));
      }
    }
    const queryString = searchParams.toString();
    if (queryString) {
      url += (url.includes('?') ? '&' : '?') + queryString;
    }
  }

  const defaultHeaders: Record<string, string> = {
    'Accept': 'application/json',
  };

  if (restOptions.body && typeof restOptions.body === 'string') {
    defaultHeaders['Content-Type'] = 'application/json';
  }

  const finalHeaders = {
    ...defaultHeaders,
    ...headers,
  };

  try {
    const response = await fetch(url, {
      headers: finalHeaders,
      ...restOptions,
    });

    if (!response.ok) {
      let errorMessage = `HTTP error ${response.status}: ${response.statusText}`;
      let errorData: unknown = null;

      try {
        errorData = await response.json();
        if (errorData && typeof errorData === 'object' && 'detail' in errorData) {
          const detail = (errorData as { detail: unknown }).detail;
          if (typeof detail === 'string') {
            errorMessage = detail;
          } else if (Array.isArray(detail)) {
            // Pydantic validation errors array
            errorMessage = detail.map((err) => (typeof err === 'object' && err?.msg ? err.msg : JSON.stringify(err))).join('; ');
          }
        }
      } catch {
        // Fallback to text if JSON parsing fails
        const text = await response.text().catch(() => '');
        if (text) errorMessage = text;
      }

      throw new ApiError(errorMessage, response.status, errorData);
    }

    // 204 No Content
    if (response.status === 204) {
      return {} as T;
    }

    return (await response.json()) as T;
  } catch (error: unknown) {
    if (error instanceof ApiError) {
      throw error;
    }

    // Handle AbortError without logging as crash
    if (error instanceof DOMException && error.name === 'AbortError') {
      throw error;
    }

    const message = error instanceof Error ? error.message : 'Network request failed';
    throw new ApiError(message, 0);
  }
}
