import { useState, useEffect } from 'react';
import useSound from 'use-sound';

export function use_resizable(default_width: string) {
  const [width, set_width] = useState(default_width);
  const [is_resizing, set_is_resizing] = useState(false);
  const [initial_x, set_initial_x] = useState(0);
  const [start_width, set_start_width] = useState(0);
  const [play_drag_end] = useSound('/sounds/book.wav');

  useEffect(() => {
    const saved_width = sessionStorage.getItem('chat_width');
    if (saved_width) {
      set_width(saved_width);
    }
  }, []);

  useEffect(() => {
    sessionStorage.setItem('chat_width', width);
  }, [width]);

  const start_resizing = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) {
      set_is_resizing(true);
      set_initial_x(e.clientX);
      set_start_width(parseFloat(width));
    }
  };

  const stop_resizing = () => {
    if (is_resizing) {
      set_is_resizing(false);
      play_drag_end();
    }
  };

  useEffect(() => {
    const handle_mouse_move = (e: MouseEvent) => {
      if (is_resizing) {
        const diff = initial_x - e.clientX;
        const new_width = Math.max(0, Math.min(100, start_width + (diff / window.innerWidth) * 100));
        set_width(`${new_width}%`);
      }
    };

    document.addEventListener('mousemove', handle_mouse_move);
    document.addEventListener('mouseup', stop_resizing);

    return () => {
      document.removeEventListener('mousemove', handle_mouse_move);
      document.removeEventListener('mouseup', stop_resizing);
    };
  }, [is_resizing, initial_x, start_width, play_drag_end]);

  return { width, start_resizing };
}