import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MessageBubble } from '../../components/MessageBubble';

describe('MessageBubble', () => {
  it('renders user message with right-aligned styling', () => {
    const { container } = render(<MessageBubble text="Hello!" isUser={true} />);
    const messageDiv = container.querySelector('.message.user');
    
    expect(messageDiv).toBeInTheDocument();
    expect(screen.getByText('Hello!')).toBeInTheDocument();
  });

  it('does not display avatar for user messages', () => {
    const { container } = render(<MessageBubble text="Hello!" isUser={true} />);
    const avatar = container.querySelector('.avatar');
    
    expect(avatar).not.toBeInTheDocument();
  });

  it('renders agent message with left-aligned styling', () => {
    const { container } = render(<MessageBubble text="Hi there!" isUser={false} />);
    const messageDiv = container.querySelector('.message.agent');
    
    expect(messageDiv).toBeInTheDocument();
    expect(screen.getByText('Hi there!')).toBeInTheDocument();
  });

  it('displays avatar for agent messages', () => {
    const { container } = render(<MessageBubble text="Hi there!" isUser={false} />);
    const avatar = container.querySelector('.avatar');
    
    expect(avatar).toBeInTheDocument();
    expect(avatar).toHaveTextContent('B');
  });

  it('displays message text correctly', () => {
    const longText = 'This is a longer message with multiple words and punctuation!';
    const { rerender } = render(<MessageBubble text="Short" isUser={true} />);
    
    expect(screen.getByText('Short')).toBeInTheDocument();
    
    rerender(<MessageBubble text={longText} isUser={false} />);
    
    expect(screen.getByText(longText)).toBeInTheDocument();
  });

  it('applies message-bubble class with correct variant', () => {
    const { container: userContainer } = render(
      <MessageBubble text="User msg" isUser={true} />
    );
    
    expect(userContainer.querySelector('.message-bubble.user')).toBeInTheDocument();
    
    const { container: agentContainer } = render(
      <MessageBubble text="Agent msg" isUser={false} />
    );
    
    expect(agentContainer.querySelector('.message-bubble.agent')).toBeInTheDocument();
  });

  it('handles empty text', () => {
    const { container } = render(<MessageBubble text="" isUser={true} />);
    const messageBubble = container.querySelector('.message-bubble');
    
    expect(messageBubble).toBeInTheDocument();
    expect(messageBubble?.textContent).toBe('');
  });

  it('handles text with special characters', () => {
    const specialText = 'Test with <special> & "characters"';
    render(<MessageBubble text={specialText} isUser={true} />);
    
    expect(screen.getByText(specialText)).toBeInTheDocument();
  });
});
