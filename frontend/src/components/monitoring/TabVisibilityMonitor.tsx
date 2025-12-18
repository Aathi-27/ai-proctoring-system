import { useEffect, useRef } from 'react';
import { MonitoringEventType } from '../../types/monitoring';
import { monitoringEventEmitter } from '../../lib/eventEmitter';

interface TabVisibilityMonitorProps {
  enabled: boolean;
  sessionId: string;
  candidateId: string;
}

export const TabVisibilityMonitor: React.FC<TabVisibilityMonitorProps> = ({
  enabled,
  sessionId,
  candidateId,
}) => {
  const hiddenTimeRef = useRef<number | null>(null);

  useEffect(() => {
    if (!enabled || typeof window === 'undefined') return;

    const handleVisibilityChange = () => {
      const now = Date.now();

      if (document.hidden) {
        hiddenTimeRef.current = now;
      } else {
        if (hiddenTimeRef.current) {
          const inactiveDuration = now - hiddenTimeRef.current;
          
          monitoringEventEmitter.emit({
            type: MonitoringEventType.TAB_SWITCHED,
            timestamp: now,
            inactive_duration: inactiveDuration,
            sessionId,
            candidateId,
          });

          hiddenTimeRef.current = null;
        }
      }
    };

    const handleWindowBlur = () => {
      if (!hiddenTimeRef.current) {
        hiddenTimeRef.current = Date.now();
      }
    };

    const handleWindowFocus = () => {
      if (hiddenTimeRef.current) {
        const now = Date.now();
        const inactiveDuration = now - hiddenTimeRef.current;
        
        monitoringEventEmitter.emit({
          type: MonitoringEventType.TAB_SWITCHED,
          timestamp: now,
          inactive_duration: inactiveDuration,
          sessionId,
          candidateId,
        });

        hiddenTimeRef.current = null;
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('blur', handleWindowBlur);
    window.addEventListener('focus', handleWindowFocus);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('blur', handleWindowBlur);
      window.removeEventListener('focus', handleWindowFocus);
      hiddenTimeRef.current = null;
    };
  }, [enabled, sessionId, candidateId]);

  return null;
};
