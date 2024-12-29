import axios from 'axios';
import type { SearchQuery, SearchResponse } from '@/types/search';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for logging in development
if (process.env.NODE_ENV === 'development') {
  api.interceptors.request.use(request => {
    console.log('API Request:', request);
    return request;
  });
}

export const searchPapers = async (query: string): Promise<SearchResponse> => {
  try {
    const searchQuery: SearchQuery = { query };
    const response = await api.post<SearchResponse>('/search', searchQuery);
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      if (error.response?.status === 429) {
        throw {
          status: 429,
          message: error.response.data.detail || 'Rate limit exceeded'
        };
      }
      console.error('API Error:', error.response?.data);
    }
    throw error;
  }
};