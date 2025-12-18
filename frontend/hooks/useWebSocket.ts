import { useState, useEffect, useRef, useCallback } from 'react';
import { WebSocketClient, MessageType, ConnectionState, createWebSocketURL } from '@/lib/websocket';

export interface UseWebSocketOptions {
  url: string;
  autoConnect?: boolean;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}

export function useWebSocket(options: UseWebSocketOptions) {
  const [connectionState, setConnectionState] = useState<ConnectionState>('disconnected');
  const [lastMessage, setLastMessage] = useState<any>(null);
  const clientRef = useRef<WebSocketClient | null>(null);

  useEffect(() => {
    clientRef.current = new WebSocketClient({
      url: options.url,
      reconnectInterval: options.reconnectInterval,
      maxReconnectAttempts: options.maxReconnectAttempts
    });

    const unsubscribe = clientRef.current.onStateChange((state) => {
      setConnectionState(state);
    });

    if (options.autoConnect) {
      clientRef.current.connect();
    }

    return () => {
      unsubscribe();
      if (clientRef.current) {
        clientRef.current.disconnect();
      }
    };
  }, [options.url]);

  const connect = useCallback(() => {
    if (clientRef.current) {
      clientRef.current.connect();
    }
  }, []);

  const disconnect = useCallback(() => {
    if (clientRef.current) {
      clientRef.current.disconnect();
    }
  }, []);

  const send = useCallback((type: MessageType, data: any) => {
    if (clientRef.current) {
      return clientRef.current.send(type, data);
    }
    return false;
  }, []);

  const on = useCallback((type: MessageType, handler: (data: any) => void) => {
    if (clientRef.current) {
      return clientRef.current.on(type, handler);
    }
    return () => {};
  }, []);

  const sendVideoFrame = useCallback((sessionId: string, frameData: string, frameNumber: number, quality: string) => {
    if (clientRef.current) {
      return clientRef.current.sendVideoFrame(sessionId, frameData, frameNumber, quality);
    }
    return false;
  }, []);

  const sendAudioChunk = useCallback((sessionId: string, audioData: string, chunkNumber: number, sampleRate: number) => {
    if (clientRef.current) {
      return clientRef.current.sendAudioChunk(sessionId, audioData, chunkNumber, sampleRate);
    }
    return false;
  }, []);

  const sendCandidateStatus = useCallback((sessionId: string, status: string, hasVideo: boolean, hasAudio: boolean, networkQuality: string) => {
    if (clientRef.current) {
      return clientRef.current.sendCandidateStatus(sessionId, status, hasVideo, hasAudio, networkQuality);
    }
    return false;
  }, []);

  const sendPermissionGranted = useCallback(() => {
    if (clientRef.current) {
      return clientRef.current.sendPermissionGranted();
    }
    return false;
  }, []);

  const sendPermissionDenied = useCallback((reason?: string) => {
    if (clientRef.current) {
      return clientRef.current.sendPermissionDenied(reason);
    }
    return false;
  }, []);

  const sendStreamQuality = useCallback((sessionId: string, videoQuality: string, fps: number, bandwidthKbps: number) => {
    if (clientRef.current) {
      return clientRef.current.sendStreamQuality(sessionId, videoQuality, fps, bandwidthKbps);
    }
    return false;
  }, []);

  return {
    connectionState,
    isConnected: connectionState === 'connected',
    lastMessage,
    connect,
    disconnect,
    send,
    on,
    sendVideoFrame,
    sendAudioChunk,
    sendCandidateStatus,
    sendPermissionGranted,
    sendPermissionDenied,
    sendStreamQuality,
    client: clientRef.current
  };
}
