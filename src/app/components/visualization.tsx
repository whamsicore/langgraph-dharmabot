'use client';

import { useEffect, useRef } from 'react';

export default function Visualization() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (canvas) {
      const ctx = canvas.getContext('2d');
      if (ctx) {
        // Set canvas size
        canvas.width = canvas.offsetWidth;
        canvas.height = canvas.offsetHeight;

        // Example visualization (a simple pulsating circle)
        let hue = 0;
        const animate = () => {
          ctx.fillStyle = 'rgba(0, 0, 0, 0.1)';
          ctx.fillRect(0, 0, canvas.width, canvas.height);

          const centerX = canvas.width / 2;
          const centerY = canvas.height / 2;
          const radius = 50 + Math.sin(Date.now() / 500) * 20;

          ctx.beginPath();
          ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
          ctx.fillStyle = `hsl(${hue}, 100%, 50%)`;
          ctx.fill();

          hue = (hue + 1) % 360;

          requestAnimationFrame(animate);
        };

        animate();
      }
    }
  }, []);

  return (
    <div className="w-full h-full bg-gray-900">
      <canvas ref={canvasRef} className="w-full h-full" />
    </div>
  );
}