import React, { useState } from 'react';
import { Send, Loader2 } from 'lucide-react';
import Message from './Messaging';

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');
    
    const messageId = Date.now();
    
    const updatedMessages = [
      ...messages,
      { id: messageId, role: 'user', content: userMessage }
    ];
    setMessages(updatedMessages);
    setIsLoading(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userMessage }),
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || 'Failed to get response');
      }

      setMessages(currentMessages => [
        ...currentMessages,
        { id: messageId, role: 'assistant', content: data.response }
      ]);
    } catch (error) {
      console.error('Error:', error);
      setMessages(currentMessages => [
        ...currentMessages,
        { 
          id: messageId,
          role: 'assistant', 
          content: 'Sorry, there was an error processing your request.' 
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full h-screen flex flex-col bg-gray-900">
      <div className="w-full bg-gray-800 p-4 text-center border-b border-gray-700">
        <h1 className="text-2xl font-bold text-white">Custom SwornChat Bot</h1>
      </div>

      <div className="flex-1 w-full overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <Message
            key={message.id}
            message={message}
            isUser={message.role === 'user'}
          />
        ))}
        {isLoading && (
          <div className="w-full flex justify-center">
            <Loader2 className="h-6 w-6 text-white animate-spin" />
          </div>
        )}
      </div>

      <div className="w-full p-4 bg-gray-800">
        <form onSubmit={handleSubmit} className="flex gap-2 w-full">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            className="flex-1 p-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-gray-700 text-white"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading}
            className="p-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-blue-300"
          >
            <Send size={20} />
          </button>
        </form>
      </div>
    </div>
  );
};

export default ChatInterface;