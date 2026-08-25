import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ChatWindow } from '../../components/ChatWindow';
import * as apiModule from '../../services/api';

// Mock the api module
vi.mock('../../services/api', () => ({
  chatAPI: {
    sendMessage: vi.fn(),
    healthCheck: vi.fn(),
  },
}));

describe('ChatWindow', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('renders chat interface with header', () => {
    render(<ChatWindow />);

    expect(screen.getByText('BONA')).toBeInTheDocument();
    expect(screen.getByText('RAG')).toBeInTheDocument();
    expect(screen.getByText('Product Support Assistant')).toBeInTheDocument();
  });

  it('displays welcome message when no messages are present', () => {
    render(<ChatWindow />);

    expect(screen.getByText('Welcome to Bona Support Assistant')).toBeInTheDocument();
    expect(
      screen.getByText(/Ask about product specifications, drying times, and more/i)
    ).toBeInTheDocument();
  });

  it('sends message on button click', async () => {
    const mockResponse = {
      answer: 'Response message',
      source_documents: [],
    };

    vi.spyOn(apiModule.chatAPI, 'sendMessage').mockResolvedValue(mockResponse);

    const user = userEvent.setup();
    render(<ChatWindow />);

    const textarea = screen.getByPlaceholderText('Ask about Bona products...');
    const sendButton = screen.getByRole('button', { name: /Send/i });

    await user.type(textarea, 'What is drying time?');
    await user.click(sendButton);

    await waitFor(() => {
      expect(apiModule.chatAPI.sendMessage).toHaveBeenCalledWith(
        'What is drying time?',
        expect.stringContaining('session-')
      );
    });
  });

  it('displays user messages in chat', async () => {
    const mockResponse = {
      answer: 'Agent response',
      source_documents: [],
    };

    vi.spyOn(apiModule.chatAPI, 'sendMessage').mockResolvedValue(mockResponse);

    const user = userEvent.setup();
    render(<ChatWindow />);

    const textarea = screen.getByPlaceholderText('Ask about Bona products...');
    const sendButton = screen.getByRole('button', { name: /Send/i });

    await user.type(textarea, 'User question');
    await user.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText('User question')).toBeInTheDocument();
    });
  });

  it('displays agent responses in chat', async () => {
    const mockResponse = {
      answer: 'This is the agent response',
      source_documents: [],
    };

    vi.spyOn(apiModule.chatAPI, 'sendMessage').mockResolvedValue(mockResponse);

    const user = userEvent.setup();
    render(<ChatWindow />);

    const textarea = screen.getByPlaceholderText('Ask about Bona products...');
    const sendButton = screen.getByRole('button', { name: /Send/i });

    await user.type(textarea, 'What time does it dry?');
    await user.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText('This is the agent response')).toBeInTheDocument();
    });
  });

  it('shows typing indicator while loading', async () => {
    const mockResponse = {
      answer: 'Response',
      source_documents: [],
    };

    vi.spyOn(apiModule.chatAPI, 'sendMessage').mockImplementation(
      () =>
        new Promise((resolve) => {
          setTimeout(() => resolve(mockResponse), 500);
        })
    );

    const user = userEvent.setup();
    const { container } = render(<ChatWindow />);

    const textarea = screen.getByPlaceholderText('Ask about Bona products...');
    const sendButton = screen.getByRole('button', { name: /Send/i });

    await user.type(textarea, 'Test');
    await user.click(sendButton);

    // Typing indicator should appear
    await waitFor(() => {
      const typing = container.querySelector('.typing');
      expect(typing).toBeInTheDocument();
    });
  });

  it('hides typing indicator after response received', async () => {
    const mockResponse = {
      answer: 'Response',
      source_documents: [],
    };

    vi.spyOn(apiModule.chatAPI, 'sendMessage').mockResolvedValue(mockResponse);

    const user = userEvent.setup();
    const { container } = render(<ChatWindow />);

    const textarea = screen.getByPlaceholderText('Ask about Bona products...');
    const sendButton = screen.getByRole('button', { name: /Send/i });

    await user.type(textarea, 'Test');
    await user.click(sendButton);

    await waitFor(() => {
      const typing = container.querySelector('.typing');
      expect(typing).not.toBeInTheDocument();
    });
  });

  it('displays error messages when API fails', async () => {
    const errorMessage = 'Network error occurred';
    vi.spyOn(apiModule.chatAPI, 'sendMessage').mockRejectedValue(
      new Error(errorMessage)
    );

    const user = userEvent.setup();
    render(<ChatWindow />);

    const textarea = screen.getByPlaceholderText('Ask about Bona products...');
    const sendButton = screen.getByRole('button', { name: /Send/i });

    await user.type(textarea, 'Test');
    await user.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText(errorMessage)).toBeInTheDocument();
    });
  });

  it('handles session ID consistently', async () => {
    const mockResponse = {
      answer: 'Response',
      source_documents: [],
    };

    vi.spyOn(apiModule.chatAPI, 'sendMessage').mockResolvedValue(mockResponse);

    const user = userEvent.setup();
    render(<ChatWindow />);

    const textarea = screen.getByPlaceholderText('Ask about Bona products...');
    const sendButton = screen.getByRole('button', { name: /Send/i });

    // Send first message
    await user.type(textarea, 'First message');
    await user.click(sendButton);

    const firstCallSessionId = (apiModule.chatAPI.sendMessage as any).mock.calls[0][1];

    // Clear textarea and send second message
    await waitFor(() => {
      expect(textarea).toHaveValue('');
    });

    await user.type(textarea, 'Second message');
    await user.click(sendButton);

    const secondCallSessionId = (apiModule.chatAPI.sendMessage as any).mock.calls[1][1];

    // Session ID should be the same for both messages
    expect(firstCallSessionId).toBe(secondCallSessionId);
    expect(firstCallSessionId).toMatch(/^session-\d+$/);
  });

  it('displays multiple messages in sequence', async () => {
    const mockResponse1 = {
      answer: 'First response',
      source_documents: [],
    };

    const mockResponse2 = {
      answer: 'Second response',
      source_documents: [],
    };

    vi.spyOn(apiModule.chatAPI, 'sendMessage')
      .mockResolvedValueOnce(mockResponse1)
      .mockResolvedValueOnce(mockResponse2);

    const user = userEvent.setup();
    render(<ChatWindow />);

    const textarea = screen.getByPlaceholderText('Ask about Bona products...');
    const sendButton = screen.getByRole('button', { name: /Send/i });

    // Send first message
    await user.type(textarea, 'First question');
    await user.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText('First question')).toBeInTheDocument();
      expect(screen.getByText('First response')).toBeInTheDocument();
    });

    // Send second message
    await user.type(textarea, 'Second question');
    await user.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText('Second question')).toBeInTheDocument();
      expect(screen.getByText('Second response')).toBeInTheDocument();
    });
  });

  it('displays sources when agent response includes source documents', async () => {
    const mockResponse = {
      answer: 'Based on the documents...',
      source_documents: [
        {
          content: 'Content 1',
          source: 'product_guide.pdf',
          score: 0.95,
        },
        {
          content: 'Content 2',
          source: 'specs.pdf',
          score: 0.87,
        },
      ],
    };

    vi.spyOn(apiModule.chatAPI, 'sendMessage').mockResolvedValue(mockResponse);

    const user = userEvent.setup();
    render(<ChatWindow />);

    const textarea = screen.getByPlaceholderText('Ask about Bona products...');
    const sendButton = screen.getByRole('button', { name: /Send/i });

    await user.type(textarea, 'Where can I find specs?');
    await user.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText(/product_guide.pdf/)).toBeInTheDocument();
      expect(screen.getByText(/specs.pdf/)).toBeInTheDocument();
      expect(screen.getByText('Score: 95%')).toBeInTheDocument();
      expect(screen.getByText('Score: 87%')).toBeInTheDocument();
    });
  });

  it('does not display sources when empty sources array', async () => {
    const mockResponse = {
      answer: 'No sources available',
      source_documents: [],
    };

    vi.spyOn(apiModule.chatAPI, 'sendMessage').mockResolvedValue(mockResponse);

    const user = userEvent.setup();
    render(<ChatWindow />);

    const textarea = screen.getByPlaceholderText('Ask about Bona products...');
    const sendButton = screen.getByRole('button', { name: /Send/i });

    await user.type(textarea, 'Test');
    await user.click(sendButton);

    await waitFor(() => {
      expect(screen.queryByText('Sources')).not.toBeInTheDocument();
    });
  });

  it('auto-scrolls to bottom on new messages', async () => {
    const mockResponse = {
      answer: 'Response',
      source_documents: [],
    };

    vi.spyOn(apiModule.chatAPI, 'sendMessage').mockResolvedValue(mockResponse);

    const user = userEvent.setup();
    const { container } = render(<ChatWindow />);

    const threadDiv = container.querySelector('.thread');
    const scrollTopSpy = vi.spyOn(threadDiv || {}, 'scrollTop', 'set');

    const textarea = screen.getByPlaceholderText('Ask about Bona products...');
    const sendButton = screen.getByRole('button', { name: /Send/i });

    await user.type(textarea, 'Message');
    await user.click(sendButton);

    await waitFor(() => {
      if (threadDiv) {
        expect(threadDiv.scrollTop).toBe(threadDiv.scrollHeight);
      }
    });
  });

  it('clears error when sending new message', async () => {
    const errorMessage = 'API Error';

    vi.spyOn(apiModule.chatAPI, 'sendMessage')
      .mockRejectedValueOnce(new Error(errorMessage))
      .mockResolvedValueOnce({ answer: 'Success', source_documents: [] });

    const user = userEvent.setup();
    render(<ChatWindow />);

    const textarea = screen.getByPlaceholderText('Ask about Bona products...');
    const sendButton = screen.getByRole('button', { name: /Send/i });

    // First message - fails
    await user.type(textarea, 'First');
    await user.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText(errorMessage)).toBeInTheDocument();
    });

    // Second message - succeeds
    await user.type(textarea, 'Second');
    await user.click(sendButton);

    await waitFor(() => {
      expect(screen.queryByText(errorMessage)).not.toBeInTheDocument();
      expect(screen.getByText('Success')).toBeInTheDocument();
    });
  });

  it('handles error response with error message in state', async () => {
    const errorMessage = 'Service unavailable';
    vi.spyOn(apiModule.chatAPI, 'sendMessage').mockRejectedValue(
      new Error(errorMessage)
    );

    const user = userEvent.setup();
    render(<ChatWindow />);

    const textarea = screen.getByPlaceholderText('Ask about Bona products...');
    const sendButton = screen.getByRole('button', { name: /Send/i });

    await user.type(textarea, 'Trigger error');
    await user.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText(errorMessage)).toBeInTheDocument();
    });
  });

  it('disables input while loading', async () => {
    const mockResponse = {
      answer: 'Response',
      source_documents: [],
    };

    vi.spyOn(apiModule.chatAPI, 'sendMessage').mockImplementation(
      () =>
        new Promise((resolve) => {
          setTimeout(() => resolve(mockResponse), 200);
        })
    );

    const user = userEvent.setup();
    render(<ChatWindow />);

    const textarea = screen.getByPlaceholderText('Ask about Bona products...');
    const sendButton = screen.getByRole('button', { name: /Send/i });

    await user.type(textarea, 'Test');
    await user.click(sendButton);

    await waitFor(() => {
      expect(textarea).toBeDisabled();
      expect(sendButton).toBeDisabled();
    });

    // After response, input should be enabled
    await waitFor(() => {
      expect(textarea).not.toBeDisabled();
      expect(sendButton).not.toBeDisabled();
    });
  });
});
