'use client';

import { useEffect, useRef } from 'react';

export interface VideoPreviewProps {
  stream: MediaStream | null;
  mirrored?: boolean;
  muted?: boolean;
  width?: string;
  height?: string;
}

export default function VideoPreview({
  stream,
  mirrored = true,
  muted = true,
  width = '100%',
  height = 'auto'
}: VideoPreviewProps) {
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    if (videoRef.current && stream) {
      videoRef.current.srcObject = stream;
      videoRef.current.play().catch(err => {
        console.error('Error playing video:', err);
      });
    }

    return () => {
      if (videoRef.current) {
        videoRef.current.srcObject = null;
      }
    };
  }, [stream]);

  if (!stream) {
    return (
      <div style={{
        width,
        height: height === 'auto' ? '400px' : height,
        backgroundColor: '#1a1a1a',
        borderRadius: '8px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: '#888',
        fontSize: '14px'
      }}>
        No video stream available
      </div>
    );
  }

  return (
    <div style={{
      width,
      height,
      position: 'relative',
      borderRadius: '8px',
      overflow: 'hidden',
      backgroundColor: '#000'
    }}>
      <video
        ref={videoRef}
        autoPlay
        playsInline
        muted={muted}
        style={{
          width: '100%',
          height: '100%',
          objectFit: 'cover',
          transform: mirrored ? 'scaleX(-1)' : 'none'
        }}
      />
      <div style={{
        position: 'absolute',
        bottom: '12px',
        left: '12px',
        padding: '6px 12px',
        backgroundColor: 'rgba(0, 0, 0, 0.7)',
        borderRadius: '4px',
        color: 'white',
        fontSize: '12px',
        display: 'flex',
        alignItems: 'center',
        gap: '6px'
      }}>
        <span style={{
          width: '8px',
          height: '8px',
          borderRadius: '50%',
          backgroundColor: '#00ff00',
          animation: 'pulse 2s ease-in-out infinite'
        }} />
        <style jsx>{`
          @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
          }
        `}</style>
        Live
      </div>
    </div>
  );
}
