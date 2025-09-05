// components/MarkdownRenderer.jsx
import React from 'react';
import ReactMarkdown from 'react-markdown';
import './MarkdownRenderer.css';

export default function MarkdownRenderer({ content }) {
  return (
    <div className="message-text-container">
      <ReactMarkdown
        components={{
          strong: ({node, ...props}) => <strong className="text-bold" {...props} />,
          em: ({node, ...props}) => <em className="text-italic" {...props} />,
          del: ({node, ...props}) => <del className="text-strikethrough" {...props} />,
          code: ({node, ...props}) => <code className="text-code" {...props} />,
          p: ({node, ...props}) => <p className="text-paragraph" {...props} />
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}


