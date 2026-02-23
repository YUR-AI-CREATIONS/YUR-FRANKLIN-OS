import React, { useEffect, useRef } from 'react';

/**
 * NeuralBrain - 3D rotating neural network visualization
 * Shows synaptic firing activity, speeds up when "thinking"
 * 
 * @param {string} themeColor - Hex color for the brain (e.g., '#00ff88')
 * @param {boolean} isThinking - When true, brain activity increases
 * @param {string} size - 'sm', 'md', 'lg' for different sizes
 */
const NeuralBrain = ({ themeColor = '#00ff88', isThinking = false, size = 'md' }) => {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrameId;
    let time = 0;

    // Brain parameters
    const points = [];
    const numPoints = size === 'sm' ? 60 : size === 'lg' ? 150 : 120;
    const connections = [];

    // Create a sphere-like cluster of points for the brain lobes
    for (let i = 0; i < numPoints; i++) {
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(Math.random() * 2 - 1);
      // Shape it a bit like a brain (two lobes)
      const lobeShift = (Math.random() > 0.5 ? 0.4 : -0.4);
      const r = 0.8 + Math.random() * 0.4;
      
      const x = r * Math.sin(phi) * Math.cos(theta) + lobeShift;
      const y = r * Math.sin(phi) * Math.sin(theta) * 0.8; // Flattened
      const z = r * Math.cos(phi);

      points.push({ x, y, z, ox: x, oy: y, oz: z });
    }

    // Create neural connections based on proximity
    for (let i = 0; i < points.length; i++) {
      for (let j = i + 1; j < points.length; j++) {
        const d = Math.sqrt(
          Math.pow(points[i].ox - points[j].ox, 2) +
          Math.pow(points[i].oy - points[j].oy, 2) +
          Math.pow(points[i].oz - points[j].oz, 2)
        );
        if (d < 0.6) {
          connections.push([i, j]);
        }
      }
    }

    const init = () => {
      const container = canvas.parentElement;
      if (container) {
        canvas.width = container.clientWidth;
        canvas.height = container.clientHeight;
      }
    };

    const draw = () => {
      time += isThinking ? 0.04 : 0.015;
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      const centerX = canvas.width / 2;
      const centerY = canvas.height / 2;
      const scale = Math.min(canvas.width, canvas.height) * 0.35;

      // Rotation matrix
      const rx = time * 0.3;
      const ry = time * 0.5;

      const projectedPoints = points.map(p => {
        // Undulation
        const offset = Math.sin(time + p.ox * 2) * 0.05;
        let x = p.ox * (1 + offset);
        let y = p.oy * (1 + offset);
        let z = p.oz * (1 + offset);

        // Rotate Y
        const y_z = z * Math.cos(ry) - x * Math.sin(ry);
        const y_x = z * Math.sin(ry) + x * Math.cos(ry);
        x = y_x; z = y_z;

        // Rotate X
        const x_y = y * Math.cos(rx) - z * Math.sin(rx);
        const x_z = y * Math.sin(rx) + z * Math.cos(rx);
        y = x_y; z = x_z;

        // Project
        const perspective = 1000 / (1000 + z * scale);
        return {
          x: centerX + x * scale * perspective,
          y: centerY + y * scale * perspective,
          z: z,
          p: perspective
        };
      });

      // Draw Connections (Synapses)
      ctx.lineWidth = 0.5;
      connections.forEach(([i, j]) => {
        const p1 = projectedPoints[i];
        const p2 = projectedPoints[j];
        
        // Depth-based opacity
        const opacity = Math.max(0, (p1.z + p2.z + 2) / 4);
        const alphaHex = Math.floor(opacity * 20).toString(16).padStart(2, '0');
        ctx.strokeStyle = `${themeColor}${alphaHex}`;
        
        ctx.beginPath();
        ctx.moveTo(p1.x, p1.y);
        ctx.lineTo(p2.x, p2.y);
        ctx.stroke();

        // Random firing pulses - more frequent when thinking
        if (Math.random() > (isThinking ? 0.92 : 0.995)) {
           const pulsePos = (Math.sin(time * 5 + i) + 1) / 2;
           const px = p1.x + (p2.x - p1.x) * pulsePos;
           const py = p1.y + (p2.y - p1.y) * pulsePos;
           ctx.fillStyle = themeColor;
           ctx.beginPath();
           ctx.arc(px, py, isThinking ? 2 : 1.5, 0, Math.PI * 2);
           ctx.fill();
        }
      });

      // Draw Nodes
      projectedPoints.forEach(p => {
        const opacity = Math.max(0, (p.z + 1.5) / 3);
        const alphaHex = Math.floor(opacity * 80).toString(16).padStart(2, '0');
        ctx.fillStyle = `${themeColor}${alphaHex}`;
        ctx.beginPath();
        ctx.arc(p.x, p.y, 2 * p.p, 0, Math.PI * 2);
        ctx.fill();

        // Bright nodes in front
        if (opacity > 0.8) {
          ctx.shadowBlur = 10;
          ctx.shadowColor = themeColor;
          ctx.fillStyle = '#fff';
          ctx.beginPath();
          ctx.arc(p.x, p.y, 0.5 * p.p, 0, Math.PI * 2);
          ctx.fill();
          ctx.shadowBlur = 0;
        }
      });

      // Core Glow
      const gradient = ctx.createRadialGradient(centerX, centerY, 0, centerX, centerY, scale * 1.2);
      gradient.addColorStop(0, `${themeColor}${isThinking ? '33' : '11'}`);
      gradient.addColorStop(1, 'transparent');
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      animationFrameId = requestAnimationFrame(draw);
    };

    window.addEventListener('resize', init);
    init();
    draw();

    return () => {
      window.removeEventListener('resize', init);
      cancelAnimationFrame(animationFrameId);
    };
  }, [themeColor, isThinking, size]);

  return <canvas ref={canvasRef} className="w-full h-full block" />;
};

export default NeuralBrain;
