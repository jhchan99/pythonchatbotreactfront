import React from 'react';
import ReactMarkdown from 'react-markdown';

const Message = ({ message, isUser }) => {
  return (
    <div
      className={`w-full p-4 rounded-lg ${
        isUser
          ? 'bg-blue-100 text-gray-900'
          : 'bg-gray-100 text-gray-900'
      }`}
    >
      <div className="prose prose-sm max-w-none dark:prose-invert">
        <ReactMarkdown>{message.content}</ReactMarkdown>
      </div>
    </div>
  );
};

export default Message;