import React, { useState, useRef, useEffect } from 'react';
import { MessageBubble } from './MessageBubble';
import { InputComposer } from './InputComposer';
import { SourcesDisplay } from './SourcesDisplay';
import { chatAPI, ChatResponse, RetrievedDocument } from '../services/api';

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  sources?: RetrievedDocument[];
}

export function ChatWindow() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionId] = useState(() => `session-${Date.now()}`);
  const threadRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Auto-scroll to bottom
    if (threadRef.current) {
      setTimeout(() => {
        if (threadRef.current) {
          threadRef.current.scrollTop = threadRef.current.scrollHeight;
        }
      }, 0);
    }
  }, [messages]);

  const handleSendMessage = async (query: string) => {
    setError(null);

    // Add user message
    const userMessageId = `msg-${Date.now()}`;
    setMessages((prev) => [
      ...prev,
      {
        id: userMessageId,
        text: query,
        isUser: true,
      },
    ]);

    setIsLoading(true);

    try {
      // Call API
      const response: ChatResponse = await chatAPI.sendMessage(query, sessionId);

      // Add agent response
      const agentMessageId = `msg-${Date.now() + 1}`;
      setMessages((prev) => [
        ...prev,
        {
          id: agentMessageId,
          text: response.answer,
          isUser: false,
          sources: response.source_documents,
        },
      ]);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to get response';
      setError(errorMessage);
      setMessages((prev) => [
        ...prev,
        {
          id: `msg-${Date.now() + 1}`,
          text: `Error: ${errorMessage}`,
          isUser: false,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-wrapper">
      {/* Header */}
      <div className="top">
        <div className="brand">
          <strong>BONA</strong>
          <span>RAG</span>
        </div>
        <div style={{ marginLeft: 'auto', fontSize: '12px', color: '#98a0a5' }}>
          Product Support Assistant
        </div>
      </div>

      {/* Messages */}
      <div className="thread" ref={threadRef}>
        {messages.length === 0 && (
          <div style={{ textAlign: 'center', color: '#999', marginTop: '40px' }}>
            <p>Welcome to Bona Support Assistant</p>
            <p style={{ fontSize: '12px' }}>Ask about product specifications, drying times, and more</p>
          </div>
        )}
        {messages.map((msg) => (
          <div key={msg.id}>
            <MessageBubble text={msg.text} isUser={msg.isUser} />
            {!msg.isUser && msg.sources && msg.sources.length > 0 && (
              <SourcesDisplay documents={msg.sources} />
            )}
          </div>
        ))}
        {isLoading && (
          <div className="message">
            <div className="avatar">B</div>
            <div className="typing">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}
      </div>

      {/* Error display */}
      {error && <div className="error" style={{ margin: '8px 18px 0', fontSize: '12px' }}>{error}</div>}

      {/* Input */}
      <InputComposer onSend={handleSendMessage} isLoading={isLoading} />
    </div>
  );
}
