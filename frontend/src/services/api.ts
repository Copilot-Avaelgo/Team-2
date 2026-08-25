import axios from 'axios';

export interface RetrievedDocument {
  content: string;
  source: string;
  score: number;
}

export interface ChatResponse {
  answer: string;
  source_documents: RetrievedDocument[];
  session_id?: string;
}

export interface ChatRequest {
  query: string;
  session_id?: string;
}

const API_BASE = import.meta.env.VITE_API_BASE || '/api';

const client = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const chatAPI = {
  async sendMessage(query: string, sessionId?: string): Promise<ChatResponse> {
    try {
      const request: ChatRequest = {
        query,
        session_id: sessionId,
      };

      const response = await client.post<ChatResponse>('/chat', request);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(error.response?.data?.detail || error.message);
      }
      throw error;
    }
  },

  async healthCheck(): Promise<boolean> {
    try {
      const response = await client.get('/health');
      return response.status === 200;
    } catch {
      return false;
    }
  },
};
