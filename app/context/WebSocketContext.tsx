'use client';

import React, { createContext, useContext, useEffect, useRef, useState, useCallback } from 'react';
import type { Alert, TimelineEvent, ExamSession, WebSocketMessage } from '@/app/types';

interface WebSocketContextType {
  isConnected: boolean;
  alerts: Alert[];
  events: TimelineEvent[];
  sessionUpdates: ExamSession[];
  scoreUpdates: Record<string, number>;
  sendMessage: (message: WebSocketMessage) => void;
  acknowledgeAlert: (alertId: string) => void;
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined);

export function WebSocketProvider({ children }: { children: React.ReactNode }) {
  const [isConnected, setIsConnected] = useState(false);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [events, setEvents] = useState<TimelineEvent[]>([]);
  const [sessionUpdates, setSessionUpdates] = useState<ExamSession[]>([]);
  const [scoreUpdates, setScoreUpdates] = useState<Record<string, number>>({});
  
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  
  const connect = useCallback(() => {
    try {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.host}/api/ws`;
      
      const ws = new WebSocket(wsUrl);
      
      ws.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current);
          reconnectTimeoutRef.current = null;
        }
      };
      
      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          
          switch (message.type) {
            case 'alert': {
              const alert = message.data as Alert;
              setAlerts(prev => {
                const filtered = prev.filter(a => a.id !== alert.id);
                return [alert, ...filtered];
              });
              
              // Auto-dismiss low priority alerts after 30 seconds
              if (alert.severity === 'low') {
                setTimeout(() => {
                  setAlerts(prev => prev.filter(a => a.id !== alert.id));
                }, 30000);
              }
              break;
            }
            
            case 'event': {
              const timelineEvent = message.data as TimelineEvent;
              setEvents(prev => [timelineEvent, ...prev].slice(0, 100));
              break;
            }
            
            case 'score_update': {
              const { sessionId, score } = message.data as { sessionId: string; score: number };
              setScoreUpdates(prev => ({ ...prev, [sessionId]: score }));
              break;
            }
            
            case 'session_update': {
              const session = message.data as ExamSession;
              setSessionUpdates(prev => {
                const index = prev.findIndex(s => s.id === session.id);
                if (index >= 0) {
                  const updated = [...prev];
                  updated[index] = session;
                  return updated;
                }
                return [session, ...prev];
              });
              break;
            }
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setIsConnected(false);
      };
      
      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);
        
        // Reconnect after 3 seconds
        reconnectTimeoutRef.current = setTimeout(() => {
          connect();
        }, 3000);
      };
      
      wsRef.current = ws;
    } catch (error) {
      console.error('Error connecting to WebSocket:', error);
      setIsConnected(false);
    }
  }, []);
  
  const sendMessage = useCallback((message: WebSocketMessage) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    }
  }, []);
  
  const acknowledgeAlert = useCallback((alertId: string) => {
    setAlerts(prev =>
      prev.map(alert =>
        alert.id === alertId ? { ...alert, isAcknowledged: true } : alert
      )
    );
    
    sendMessage({
      type: 'alert',
      data: { action: 'acknowledge', alertId }
    });
  }, [sendMessage]);
  
  useEffect(() => {
    connect();
    
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  
  return (
    <WebSocketContext.Provider
      value={{
        isConnected,
        alerts,
        events,
        sessionUpdates,
        scoreUpdates,
        sendMessage,
        acknowledgeAlert
      }}
    >
      {children}
    </WebSocketContext.Provider>
  );
}

export function useWebSocket() {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocket must be used within WebSocketProvider');
  }
  return context;
}
