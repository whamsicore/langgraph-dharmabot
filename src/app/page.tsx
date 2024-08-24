'use client';

import React from 'react';
import Chat from './components/chat';
import Visualization from './components/visualization';
import Header from './components/header';
import { Resizer } from './components/Resizer';
import { use_resizable } from './hooks/use_resizable'; // Updated import path

export default function Home() {
  const { width: chat_width, start_resizing } = use_resizable('50%');

  return (
    <div className="flex flex-col h-screen">
      <Header />
      <main className="flex flex-1 overflow-hidden">
        <div className="bg-gray-100" style={{ width: `calc(100% - ${chat_width})` }}>
          <Visualization />
        </div>
        <Resizer on_mouse_down={start_resizing} />
        <div className="overflow-auto" style={{ width: chat_width }}>
          <Chat />
        </div>
      </main>
    </div>
  );
}