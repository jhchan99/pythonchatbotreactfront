import React from 'react';
import ReactMarkdown from 'react-markdown';

const Message = ({ message, isUser }) => {
  // Convert message content to string if it's an object
  const getMessageContent = (content) => {
    if (typeof content === 'object') {
      return content.response || JSON.stringify(content);
    }
    return content || '';
  };

  return (
    <div
      className={`w-full p-4 rounded-lg ${
        isUser
          ? 'bg-blue-100 text-gray-900'
          : 'bg-gray-100 text-gray-900'
      }`}
    >
      <div className="prose prose-sm max-w-none dark:prose-invert">
        <ReactMarkdown>{getMessageContent(message.content)}</ReactMarkdown>
        {message.sources && (
          <div className="mt-2 text-sm text-gray-600">
            <p className="font-semibold">Sources:</p>
            <ul className="list-disc pl-4">
              {message.sources.map((source, index) => (
                <li key={index}>{source}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};

export default Message;