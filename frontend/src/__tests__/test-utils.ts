import { vi } from 'vitest';
import { ChatResponse, RetrievedDocument } from '../../services/api';

/**
 * Mock data factories for testing
 */

export const mockDocument = (overrides?: Partial<RetrievedDocument>): RetrievedDocument => ({
  content: 'Sample document content',
  source: 'sample.pdf',
  score: 0.85,
  ...overrides,
});

export const mockChatResponse = (overrides?: Partial<ChatResponse>): ChatResponse => ({
  answer: 'This is a sample response from the agent.',
  source_documents: [],
  session_id: 'test-session-123',
  ...overrides,
});

export const mockDocumentWithScore = (
  filename: string,
  score: number
): RetrievedDocument => ({
  content: `Content for ${filename}`,
  source: filename,
  score,
});

export const mockMultipleDocuments = (count: number): RetrievedDocument[] => {
  return Array.from({ length: count }, (_, i) => ({
    content: `Content document ${i + 1}`,
    source: `document_${i + 1}.pdf`,
    score: 1 - i * 0.1,
  }));
};

/**
 * Mock API response helpers
 */

export const createMockChatAPI = () => {
  return {
    sendMessage: vi.fn(),
    healthCheck: vi.fn().mockResolvedValue(true),
  };
};

export const setupSuccessfulAPIResponse = (
  mockAPI: ReturnType<typeof createMockChatAPI>,
  response: ChatResponse
) => {
  mockAPI.sendMessage.mockResolvedValue(response);
};

export const setupFailedAPIResponse = (
  mockAPI: ReturnType<typeof createMockChatAPI>,
  error: Error
) => {
  mockAPI.sendMessage.mockRejectedValue(error);
};

export const setupDelayedAPIResponse = (
  mockAPI: ReturnType<typeof createMockChatAPI>,
  response: ChatResponse,
  delayMs: number = 500
) => {
  mockAPI.sendMessage.mockImplementation(
    () =>
      new Promise((resolve) => {
        setTimeout(() => resolve(response), delayMs);
      })
  );
};

/**
 * Test helpers for common assertions
 */

export const expectMessageDisplayed = (screen: any, text: string) => {
  const textElement = screen.getByText(text);
  expect(textElement).toBeInTheDocument();
  return textElement;
};

export const expectButtonDisabled = (screen: any, name: RegExp | string) => {
  const button = screen.getByRole('button', { name });
  expect(button).toBeDisabled();
  return button;
};

export const expectButtonEnabled = (screen: any, name: RegExp | string) => {
  const button = screen.getByRole('button', { name });
  expect(button).not.toBeDisabled();
  return button;
};

/**
 * Render helpers
 */

export const getTextarea = (screen: any): HTMLTextAreaElement => {
  return screen.getByPlaceholderText('Ask about Bona products...') as HTMLTextAreaElement;
};

export const getSendButton = (screen: any, loading: boolean = false) => {
  const name = loading ? /Sending/ : /Send/;
  return screen.getByRole('button', { name });
};

/**
 * Session ID helpers
 */

export const extractSessionId = (mockAPI: ReturnType<typeof createMockChatAPI>, callIndex: number = 0): string => {
  const calls = (mockAPI.sendMessage as any).mock.calls;
  if (calls.length > callIndex) {
    return calls[callIndex][1];
  }
  return '';
};

export const getAllSessionIds = (mockAPI: ReturnType<typeof createMockChatAPI>): string[] => {
  const calls = (mockAPI.sendMessage as any).mock.calls;
  return calls.map((call: any[]) => call[1]);
};
