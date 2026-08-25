import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { SourcesDisplay } from '../../components/SourcesDisplay';
import { RetrievedDocument } from '../../services/api';

describe('SourcesDisplay', () => {
  it('renders sources with file names', () => {
    const documents: RetrievedDocument[] = [
      {
        content: 'Sample content',
        source: 'product_guide.pdf',
        score: 0.95,
      },
    ];

    render(<SourcesDisplay documents={documents} />);

    expect(screen.getByText(/product_guide.pdf/)).toBeInTheDocument();
  });

  it('displays relevance score as percentage', () => {
    const documents: RetrievedDocument[] = [
      {
        content: 'Sample content',
        source: 'specs.pdf',
        score: 0.85,
      },
    ];

    render(<SourcesDisplay documents={documents} />);

    expect(screen.getByText('Score: 85%')).toBeInTheDocument();
  });

  it('displays multiple document sources', () => {
    const documents: RetrievedDocument[] = [
      {
        content: 'Content 1',
        source: 'doc1.pdf',
        score: 0.9,
      },
      {
        content: 'Content 2',
        source: 'doc2.pdf',
        score: 0.8,
      },
      {
        content: 'Content 3',
        source: 'doc3.txt',
        score: 0.75,
      },
    ];

    render(<SourcesDisplay documents={documents} />);

    expect(screen.getByText(/doc1.pdf/)).toBeInTheDocument();
    expect(screen.getByText(/doc2.pdf/)).toBeInTheDocument();
    expect(screen.getByText(/doc3.txt/)).toBeInTheDocument();
    expect(screen.getByText('Score: 90%')).toBeInTheDocument();
    expect(screen.getByText('Score: 80%')).toBeInTheDocument();
    expect(screen.getByText('Score: 75%')).toBeInTheDocument();
  });

  it('displays sources header', () => {
    const documents: RetrievedDocument[] = [
      {
        content: 'Content',
        source: 'file.pdf',
        score: 0.88,
      },
    ];

    render(<SourcesDisplay documents={documents} />);

    expect(screen.getByText('Sources')).toBeInTheDocument();
  });

  it('returns null when documents array is empty', () => {
    const { container } = render(<SourcesDisplay documents={[]} />);

    expect(container.firstChild).toBeNull();
  });

  it('returns null when documents is falsy', () => {
    const { container } = render(<SourcesDisplay documents={null as any} />);

    expect(container.firstChild).toBeNull();
  });

  it('correctly formats scores with decimal precision', () => {
    const documents: RetrievedDocument[] = [
      {
        content: 'Content',
        source: 'doc.pdf',
        score: 0.567,
      },
      {
        content: 'Content',
        source: 'doc2.pdf',
        score: 0.999,
      },
    ];

    render(<SourcesDisplay documents={documents} />);

    expect(screen.getByText('Score: 57%')).toBeInTheDocument();
    expect(screen.getByText('Score: 100%')).toBeInTheDocument();
  });

  it('renders with file icon', () => {
    const documents: RetrievedDocument[] = [
      {
        content: 'Content',
        source: 'document.pdf',
        score: 0.91,
      },
    ];

    const { container } = render(<SourcesDisplay documents={documents} />);
    const sourceFile = container.querySelector('.source-file');

    expect(sourceFile?.textContent).toContain('📄');
    expect(sourceFile?.textContent).toContain('document.pdf');
  });

  it('handles file names with special characters', () => {
    const documents: RetrievedDocument[] = [
      {
        content: 'Content',
        source: 'Product_Guide_2024-01-15.pdf',
        score: 0.92,
      },
    ];

    render(<SourcesDisplay documents={documents} />);

    expect(screen.getByText(/Product_Guide_2024-01-15.pdf/)).toBeInTheDocument();
  });

  it('applies correct CSS classes to containers', () => {
    const documents: RetrievedDocument[] = [
      {
        content: 'Content',
        source: 'file.pdf',
        score: 0.87,
      },
    ];

    const { container } = render(<SourcesDisplay documents={documents} />);

    expect(container.querySelector('.sources')).toBeInTheDocument();
    expect(container.querySelector('.sources-label')).toBeInTheDocument();
    expect(container.querySelector('.source-item')).toBeInTheDocument();
  });
});
