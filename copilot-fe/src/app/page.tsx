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

    // Clean up on unmount
    return () => {
      if (ws) {
        ws.close();
      }
    };
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
    <div className='flex justify-center gap-x-4 container mx-auto columns-1 border-b'>
      <div className="flex flex-col h-screen w-1/2">
        <div className="mb-4">
          <ul className="flex border-b">
            <li className="-mb-px mr-1">
              <a href="#" className="bg-white inline-block py-2 px-4 text-blue-500 border-l border-t border-r rounded-t hover:text-blue-700">
                Chat for Dream Mattress
              </a>
            </li>
            <li className="mr-1">
              <a href="#" className="bg-white inline-block py-2 px-4 text-gray-500 hover:text-blue-700 hover:border-b-2 hover:border-blue-500">
                Chat for Wingman
              </a>
            </li>
          </ul>
        </div>
        <div className="flex-grow overflow-y-auto">
          <div className="chat-history p-4">
            <div className="flex items-start justify-end mb-4">
              <div className="bg-gray-300 text-gray-800 p-2 rounded-lg">
                {chatHistory.map((msg, index) => (
                  <p key={index}>
                    <b>{msg.role}:</b> {msg.content}
                  </p>
                ))}
              </div>
            </div>
          </div>
        </div>

        <div className="p-4">
          <div className="flex">
            <form onSubmit={handleSubmit} className="w-full">
              <input
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Type your message here..."
                className="flex-grow border rounded-1 p-2 w-full"
              />
              <button className="w-full rounded-full p-2 px-4 py-1 text-purple-600 font-semibold rounded-full border hover:text-white hover:bg-purple-600 hover:border-transparent" type="submit">Send</button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;