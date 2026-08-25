import { RetrievedDocument } from '../services/api';

interface SourcesDisplayProps {
  documents: RetrievedDocument[];
}

export function SourcesDisplay({ documents }: SourcesDisplayProps) {
  if (!documents || documents.length === 0) {
    return null;
  }

  return (
    <div className="sources">
      <div className="sources-label">Sources</div>
      {documents.map((doc, idx) => (
        <div key={idx} className="source-item">
          <div className="source-file">📄 {doc.source}</div>
          <div style={{ fontSize: '11px', color: '#999', marginTop: '2px' }}>
            Score: {(doc.score * 100).toFixed(0)}%
          </div>
        </div>
      ))}
    </div>
  );
}
