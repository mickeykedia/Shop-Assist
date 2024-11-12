// frontend/pages/index.tsx (Next.js with TypeScript)

'use client'

import React, { useState, useEffect } from 'react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

const HomePage: React.FC = () => {
  const [message, setMessage] = useState('');
  const [chatHistory, setChatHistory] = useState<Message[]>([]);
  const [websocket, setWebsocket] = useState<WebSocket | null>(null);

  useEffect(() => {

    const ws = new WebSocket('ws://localhost:8000/chat'); // Replace with your API endpoint
    ws.onopen = () => {
      console.log('WebSocket connected');
      setWebsocket(ws)
    };

    ws.onmessage = (event) => {
      console.log("received response:");
      setChatHistory((prevHistory) => [
        ...prevHistory,
        { role: 'assistant', content: event.data.toString() }, // Ensure content is a string
      ]);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setWebsocket(null); 
    };

    return () => {
      if (ws) {
        ws.close();
      }
    };
    // Clean up on unmount
  }, []);

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    if (message.trim() !== '' && websocket) {
      setChatHistory((prevHistory) => [...prevHistory, { role: 'user', content: message }]);
      websocket.send(message);
      setMessage('');
    }
  };

  return (
    <div>
      <h1>Chat with LlamaIndex</h1>
      <div>
        {chatHistory.map((msg, index) => (
          <p key={index}>
            <b>{msg.role}:</b> {msg.content}
          </p>
        ))}
      </div>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Type your message here..."
        />
        <button type="submit">Send</button>
      </form>   

    </div>
  );
};

export default HomePage;