import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { InputComposer } from '../../components/InputComposer';

describe('InputComposer', () => {
  let onSendMock: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    onSendMock = vi.fn();
  });

  it('renders textarea with placeholder text', () => {
    render(<InputComposer onSend={onSendMock} isLoading={false} />);

    const textarea = screen.getByPlaceholderText('Ask about Bona products...');
    expect(textarea).toBeInTheDocument();
  });

  it('renders send button', () => {
    render(<InputComposer onSend={onSendMock} isLoading={false} />);

    const sendButton = screen.getByRole('button', { name: /Send/i });
    expect(sendButton).toBeInTheDocument();
  });

  it('handles text input correctly', async () => {
    const user = userEvent.setup();
    render(<InputComposer onSend={onSendMock} isLoading={false} />);

    const textarea = screen.getByPlaceholderText('Ask about Bona products...');

    await user.type(textarea, 'Hello world');

    expect(textarea).toHaveValue('Hello world');
  });

  it('calls onSend when send button is clicked with text', async () => {
    const user = userEvent.setup();
    render(<InputComposer onSend={onSendMock} isLoading={false} />);

    const textarea = screen.getByPlaceholderText('Ask about Bona products...');
    const sendButton = screen.getByRole('button', { name: /Send/i });

    await user.type(textarea, 'Test message');
    await user.click(sendButton);

    expect(onSendMock).toHaveBeenCalledWith('Test message');
    expect(onSendMock).toHaveBeenCalledTimes(1);
  });

  it('calls onSend when Enter key is pressed (not Shift+Enter)', async () => {
    const user = userEvent.setup();
    render(<InputComposer onSend={onSendMock} isLoading={false} />);

    const textarea = screen.getByPlaceholderText('Ask about Bona products...');

    await user.type(textarea, 'Test message');
    await user.keyboard('{Enter}');

    expect(onSendMock).toHaveBeenCalledWith('Test message');
  });

  it('does not send on Shift+Enter', async () => {
    const user = userEvent.setup();
    render(<InputComposer onSend={onSendMock} isLoading={false} />);

    const textarea = screen.getByPlaceholderText('Ask about Bona products...');

    await user.type(textarea, 'Line 1');
    await user.keyboard('{Shift>}{Enter}{/Shift}');

    expect(onSendMock).not.toHaveBeenCalled();
    expect(textarea).toHaveValue('Line 1\n');
  });

  it('clears input after sending', async () => {
    const user = userEvent.setup();
    render(<InputComposer onSend={onSendMock} isLoading={false} />);

    const textarea = screen.getByPlaceholderText('Ask about Bona products...');
    const sendButton = screen.getByRole('button', { name: /Send/i });

    await user.type(textarea, 'Test message');
    await user.click(sendButton);

    expect(textarea).toHaveValue('');
  });

  it('disables send button when input is empty', () => {
    render(<InputComposer onSend={onSendMock} isLoading={false} />);

    const sendButton = screen.getByRole('button');
    expect(sendButton).toBeDisabled();
  });

  it('enables send button when input has text', async () => {
    const user = userEvent.setup();
    render(<InputComposer onSend={onSendMock} isLoading={false} />);

    const textarea = screen.getByPlaceholderText('Ask about Bona products...');
    const sendButton = screen.getByRole('button');

    expect(sendButton).toBeDisabled();

    await user.type(textarea, 'Test');

    expect(sendButton).not.toBeDisabled();
  });

  it('disables send button when only whitespace is entered', async () => {
    const user = userEvent.setup();
    render(<InputComposer onSend={onSendMock} isLoading={false} />);

    const textarea = screen.getByPlaceholderText('Ask about Bona products...');
    const sendButton = screen.getByRole('button');

    await user.type(textarea, '   ');

    expect(sendButton).toBeDisabled();
  });

  it('disables send button and shows loading state when isLoading is true', () => {
    render(<InputComposer onSend={onSendMock} isLoading={true} />);

    const textarea = screen.getByPlaceholderText('Ask about Bona products...');
    const sendButton = screen.getByRole('button', { name: /Sending/i });

    expect(textarea).toBeDisabled();
    expect(sendButton).toBeDisabled();
  });

  it('displays "Sending..." text on button when loading', () => {
    render(<InputComposer onSend={onSendMock} isLoading={true} />);

    expect(screen.getByRole('button', { name: /Sending/i })).toBeInTheDocument();
  });

  it('does not send message when isLoading is true', async () => {
    const user = userEvent.setup();
    const { rerender } = render(
      <InputComposer onSend={onSendMock} isLoading={false} />
    );

    const textarea = screen.getByPlaceholderText('Ask about Bona products...');

    await user.type(textarea, 'Test message');

    rerender(<InputComposer onSend={onSendMock} isLoading={true} />);

    const sendButton = screen.getByRole('button');
    await user.click(sendButton);

    expect(onSendMock).not.toHaveBeenCalled();
  });

  it('expands textarea on multi-line input', async () => {
    const user = userEvent.setup();
    const { container } = render(
      <InputComposer onSend={onSendMock} isLoading={false} />
    );

    const textarea = screen.getByPlaceholderText('Ask about Bona products...') as HTMLTextAreaElement;
    const initialHeight = parseInt(window.getComputedStyle(textarea).height);

    await user.type(textarea, 'Line 1\nLine 2\nLine 3');

    await waitFor(() => {
      const newHeight = parseInt(window.getComputedStyle(textarea).height);
      expect(newHeight).toBeGreaterThan(initialHeight);
    });
  });

  it('does not send empty message', async () => {
    const user = userEvent.setup();
    render(<InputComposer onSend={onSendMock} isLoading={false} />);

    const textarea = screen.getByPlaceholderText('Ask about Bona products...');

    await user.type(textarea, '   ');
    await user.keyboard('{Enter}');

    expect(onSendMock).not.toHaveBeenCalled();
  });

  it('trims whitespace from message before sending', async () => {
    const user = userEvent.setup();
    render(<InputComposer onSend={onSendMock} isLoading={false} />);

    const textarea = screen.getByPlaceholderText('Ask about Bona products...');
    const sendButton = screen.getByRole('button', { name: /Send/i });

    await user.type(textarea, '  test message  ');
    await user.click(sendButton);

    expect(onSendMock).toHaveBeenCalledWith('  test message  ');
  });

  it('handles rapid successive messages', async () => {
    const user = userEvent.setup();
    render(<InputComposer onSend={onSendMock} isLoading={false} />);

    const textarea = screen.getByPlaceholderText('Ask about Bona products...');
    const sendButton = screen.getByRole('button', { name: /Send/i });

    await user.type(textarea, 'First');
    await user.click(sendButton);

    expect(onSendMock).toHaveBeenCalledTimes(1);
    expect(textarea).toHaveValue('');

    await user.type(textarea, 'Second');
    await user.click(sendButton);

    expect(onSendMock).toHaveBeenCalledTimes(2);
    expect(onSendMock).toHaveBeenNthCalledWith(2, 'Second');
  });
});
