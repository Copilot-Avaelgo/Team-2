interface MessageBubbleProps {
  text: string;
  isUser: boolean;
}

export function MessageBubble({ text, isUser }: MessageBubbleProps) {
  return (
    <div className={`message ${isUser ? 'user' : 'agent'}`}>
      {!isUser && <div className="avatar">B</div>}
      <div className={`message-bubble ${isUser ? 'user' : 'agent'}`}>
        {text}
      </div>
    </div>
  );
}
