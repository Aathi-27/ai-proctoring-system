'use client';

import type { ConnectionState } from '@/lib/websocket';

export interface ConnectionStatusProps {
  state: ConnectionState;
  showLabel?: boolean;
}

export default function ConnectionStatus({ state, showLabel = true }: ConnectionStatusProps) {
  const getStatusColor = () => {
    switch (state) {
      case 'connected':
        return '#00ff00';
      case 'connecting':
      case 'reconnecting':
        return '#ffaa00';
      case 'disconnected':
      case 'error':
        return '#ff0000';
      default:
        return '#888888';
    }
  };

  const getStatusText = () => {
    switch (state) {
      case 'connected':
        return 'Connected';
      case 'connecting':
        return 'Connecting...';
      case 'reconnecting':
        return 'Reconnecting...';
      case 'disconnected':
        return 'Disconnected';
      case 'error':
        return 'Connection Error';
      default:
        return 'Unknown';
    }
  };

  const getStatusIcon = () => {
    switch (state) {
      case 'connected':
        return '✓';
      case 'connecting':
      case 'reconnecting':
        return '⟳';
      case 'disconnected':
      case 'error':
        return '✕';
      default:
        return '?';
    }
  };

  return (
    <div style={{
      display: 'inline-flex',
      alignItems: 'center',
      gap: '8px',
      padding: '8px 12px',
      backgroundColor: 'rgba(0, 0, 0, 0.05)',
      borderRadius: '6px',
      fontSize: '14px'
    }}>
      <div style={{
        width: '12px',
        height: '12px',
        borderRadius: '50%',
        backgroundColor: getStatusColor(),
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: '8px',
        color: 'white',
        fontWeight: 'bold',
        animation: (state === 'connecting' || state === 'reconnecting') ? 'pulse 1.5s ease-in-out infinite' : 'none'
      }}>
        {state === 'connected' && ''}
      </div>
      <style jsx>{`
        @keyframes pulse {
          0%, 100% {
            opacity: 1;
            transform: scale(1);
          }
          50% {
            opacity: 0.5;
            transform: scale(1.1);
          }
        }
      `}</style>
      {showLabel && (
        <span style={{
          fontWeight: '500',
          color: '#1a1a1a'
        }}>
          {getStatusText()}
        </span>
      )}
    </div>
  );
}
