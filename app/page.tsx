'use client';

import Chat from './components/chat';
import Visualization from './components/visualization';

export default function Home() {
  return (
    <div className="flex flex-col h-screen">
      <header className="bg-gray-800 text-white p-4">
        <h1 className="text-2xl font-bold">DharmaBotUI</h1>
      </header>
      <main className="flex flex-1 overflow-hidden">
        <div className="w-1/2 bg-gray-900">
          <Visualization />
        </div>
        <div className="w-1/2 p-4 overflow-auto">
          <Chat />
        </div>
      </main>
    </div>
  );
}