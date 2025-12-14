'use client';

import { useEffect, useRef, useState } from 'react';

export interface AudioLevelVisualizerProps {
  stream: MediaStream | null;
  width?: number;
  height?: number;
  barCount?: number;
  barColor?: string;
}

export default function AudioLevelVisualizer({
  stream,
  width = 200,
  height = 40,
  barCount = 20,
  barColor = '#0066cc'
}: AudioLevelVisualizerProps) {
  const [audioLevel, setAudioLevel] = useState(0);
  const animationFrameRef = useRef<number>();
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const dataArrayRef = useRef<Uint8Array | null>(null);

  useEffect(() => {
    if (!stream) {
      return;
    }

    const audioTracks = stream.getAudioTracks();
    if (audioTracks.length === 0) {
      return;
    }

    try {
      const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext;
      audioContextRef.current = new AudioContextClass();
      analyserRef.current = audioContextRef.current.createAnalyser();
      analyserRef.current.fftSize = 256;
      
      const source = audioContextRef.current.createMediaStreamSource(stream);
      source.connect(analyserRef.current);

      const bufferLength = analyserRef.current.frequencyBinCount;
      dataArrayRef.current = new Uint8Array(bufferLength);

      const updateAudioLevel = () => {
        if (!analyserRef.current || !dataArrayRef.current) {
          return;
        }

        analyserRef.current.getByteFrequencyData(dataArrayRef.current);
        
        const sum = dataArrayRef.current.reduce((acc, val) => acc + val, 0);
        const average = sum / dataArrayRef.current.length;
        const normalizedLevel = Math.min(100, (average / 128) * 100);

        setAudioLevel(normalizedLevel);
        animationFrameRef.current = requestAnimationFrame(updateAudioLevel);
      };

      updateAudioLevel();
    } catch (error) {
      console.error('Error setting up audio visualizer:', error);
    }

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
    };
  }, [stream]);

  const bars = Array.from({ length: barCount }, (_, i) => {
    const barHeight = (audioLevel / 100) * height;
    const isActive = (i / barCount) * 100 < audioLevel;
    
    return (
      <div
        key={i}
        style={{
          width: `${(100 / barCount) - 2}%`,
          height: '100%',
          backgroundColor: isActive ? barColor : '#e0e0e0',
          borderRadius: '2px',
          transition: 'background-color 0.1s ease'
        }}
      />
    );
  });

  return (
    <div style={{ width: '100%' }}>
      <div style={{
        display: 'flex',
        alignItems: 'flex-end',
        gap: '2px',
        height: `${height}px`,
        width: `${width}px`,
        padding: '4px',
        backgroundColor: '#f5f5f5',
        borderRadius: '4px'
      }}>
        {bars}
      </div>
      <div style={{
        marginTop: '8px',
        fontSize: '12px',
        color: '#4a4a4a',
        display: 'flex',
        alignItems: 'center',
        gap: '8px'
      }}>
        <span>Audio Level:</span>
        <span style={{ fontWeight: 'bold' }}>
          {Math.round(audioLevel)}%
        </span>
        {audioLevel > 0 && (
          <span style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            backgroundColor: '#00ff00',
            display: 'inline-block'
          }} />
        )}
      </div>
    </div>
  );
}
