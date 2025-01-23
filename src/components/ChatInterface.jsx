import React, { useState, useCallback } from 'react';
import { Send, Loader2 } from 'lucide-react';
import Message from './Messaging';

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const addMessage = useCallback((message) => {
    setMessages(prevMessages => [...prevMessages, message]);
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');
    setIsLoading(true);

    // Create message objects with unique timestamps
    const timestamp = Date.now();
    const userMessageObj = {
      id: `user-${timestamp}`,
      role: 'user',
      content: userMessage,
      timestamp
    };

    try {
      // Add user message immediately
      addMessage(userMessageObj);

      // Make API call
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userMessage }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const data = await response.json();

      // Ensure we have a valid response object
      if (!data || !data.response) {
        throw new Error('Invalid response format');
      }

      // Create bot message object
      const botMessageObj = {
        id: `bot-${timestamp}`,
        role: 'assistant',
        content: data.response.response || data.response, // Handle both response formats
        sources: data.response.sources || data.sources || [], // Handle both source formats
        timestamp: timestamp + 1
      };

      // Add bot message
      addMessage(botMessageObj);

    } catch (error) {
      console.error('Chat error:', error);
      
      // Add error message
      const errorMessageObj = {
        id: `error-${timestamp}`,
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        sources: [],
        timestamp: timestamp + 1
      };
      
      addMessage(errorMessageObj);
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