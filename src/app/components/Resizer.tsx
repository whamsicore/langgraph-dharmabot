import React from 'react';

interface ResizerProps {
  on_mouse_down: (e: React.MouseEvent<HTMLDivElement>) => void;
}

export function Resizer({ on_mouse_down }: ResizerProps) {
  return (
    <div
      className="resizer"
      onMouseDown={on_mouse_down}
      style={{ cursor: 'col-resize', width: '10px' }}
    ></div>
  );
}