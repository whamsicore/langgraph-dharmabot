// This file content represents a React component called Chat, which serves as a chat interface. It manages WebSocket connections to send and receive messages, displays messages in real-time with timestamps, and provides functionality to send messages, along with sound effects for message sending and receiving. The component also handles error messages and loading indicators for a seamless chat experience within a UI.

'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import useSound from 'use-sound';
import styles from './chat.module.css';

interface Message {
  id: string;
  content: string;
  timestamp: string;
  sender_type: string;
}

export default function Chat() {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [play_send_sfx] = useSound('/sounds/menu-open.mp3');
  const [play_receive_sfx] = useSound('/sounds/keyboard/FUI Button Hi-Tech.wav');

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  const connectWebSocket = useCallback(() => {
    const ws = new WebSocket('ws://localhost:3001');
    
    ws.onopen = () => {
      console.log('WebSocket connected');
      setError(null);
    };
    ws.onmessage = (event) => {
      console.log('WebSocket message received:');
      const data = JSON.parse(event.data);
      if (data.type === 'chat') {
        setIsLoading(false);
        // play_receive_sfx();
        if (Array.isArray(data.messages)) {
          setMessages(data.messages.map(msg => ({
            ...msg,
            id: msg.id || `${msg.timestamp}-${Math.random().toString(36).substr(2, 9)}`
          })));
        } else if (data.message) {
          setMessages(prevMessages => [...prevMessages, {
            ...data.message,
            id: data.message.id || `${data.message.timestamp}-${Math.random().toString(36).substr(2, 9)}`
          }]);
        }
      }
    };
    ws.onclose = (event) => {
      console.log('WebSocket disconnected', event.reason);
      setError('WebSocket disconnected. Attempting to reconnect...');
      setTimeout(connectWebSocket, 1000);
    };
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setError('WebSocket error occurred. Check console for details.');
    };

    setSocket(ws);
  }, [play_receive_sfx]);

  useEffect(() => {
    connectWebSocket();
    return () => {
      if (socket && socket.readyState === WebSocket.OPEN) {
        socket.close();
      }
    };
  }, [connectWebSocket]);

  const sendMessage = () => {
    if (inputMessage.trim()) {
      play_send_sfx();
      
      if (socket && socket.readyState === WebSocket.OPEN) {
        const newMessage: Message = {
          id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          content: inputMessage,
          timestamp: new Date().toISOString(),
          sender_type: 'User'
        };
        
        setMessages(prevMessages => [...prevMessages, newMessage]);
        
        const messageData = {
          type: 'chat',
          content: inputMessage,
          sender_type: 'User'
        };
        socket.send(JSON.stringify(messageData));
        
        setIsLoading(true);
        setInputMessage('');
      } else {
        setError('WebSocket is not connected. Unable to send message.');
      }
    }
  };

  return (
    <div className={styles.chatContainer}>
      {error && <p className={styles.errorMessage}>{error}</p>}
      <div className={styles.messageContainer}>
        {messages.map((msg) => (
          <div key={msg.id} className={`${styles.messageWrapper} ${msg.sender_type === 'User' ? styles.userMessage : styles.systemMessage}`}>
            <div className={styles.messageBubble}>
              <span className={styles.timestamp}>{new Date(msg.timestamp).toLocaleString()}</span>
              <p className={`${styles.messageContent} text-black`}>{msg.content}</p>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className={styles.loaderWrapper}>
            <div className={styles.loader}></div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <div className={styles.inputContainer}>
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          className={`${styles.inputField} text-black`}
          placeholder="Type a message..."
        />
        <button
          onClick={sendMessage}
          className={styles.sendButton}
        >
          Send
        </button>
      </div>
    </div>
  );
}