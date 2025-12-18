import { useEffect, useRef } from 'react';
import { MonitoringEventType } from '../../types/monitoring';
import { monitoringEventEmitter } from '../../lib/eventEmitter';

interface InactivityTrackerProps {
  enabled: boolean;
  inactivityThreshold: number;
  sessionId: string;
  candidateId: string;
}

export const InactivityTracker: React.FC<InactivityTrackerProps> = ({
  enabled,
  inactivityThreshold,
  sessionId,
  candidateId,
}) => {
  const lastKeyboardActivityRef = useRef<number>(Date.now());
  const lastMouseActivityRef = useRef<number>(Date.now());
  const keyboardTimerRef = useRef<NodeJS.Timeout | null>(null);
  const mouseTimerRef = useRef<NodeJS.Timeout | null>(null);
  const keyboardInactiveRef = useRef<boolean>(false);
  const mouseInactiveRef = useRef<boolean>(false);

  useEffect(() => {
    if (!enabled || typeof window === 'undefined') return;

    const checkKeyboardInactivity = () => {
      const now = Date.now();
      const timeSinceLastActivity = now - lastKeyboardActivityRef.current;

      if (timeSinceLastActivity >= inactivityThreshold && !keyboardInactiveRef.current) {
        keyboardInactiveRef.current = true;
        
        monitoringEventEmitter.emit({
          type: MonitoringEventType.KEYBOARD_INACTIVITY,
          timestamp: now,
          duration_seconds: Math.floor(timeSinceLastActivity / 1000),
          sessionId,
          candidateId,
        });
      }
    };

    const checkMouseInactivity = () => {
      const now = Date.now();
      const timeSinceLastActivity = now - lastMouseActivityRef.current;

      if (timeSinceLastActivity >= inactivityThreshold && !mouseInactiveRef.current) {
        mouseInactiveRef.current = true;
        
        monitoringEventEmitter.emit({
          type: MonitoringEventType.MOUSE_INACTIVITY,
          timestamp: now,
          duration_seconds: Math.floor(timeSinceLastActivity / 1000),
          sessionId,
          candidateId,
        });
      }
    };

    const handleKeyboardActivity = () => {
      const wasInactive = keyboardInactiveRef.current;
      lastKeyboardActivityRef.current = Date.now();
      keyboardInactiveRef.current = false;

      if (wasInactive) {
        monitoringEventEmitter.emit({
          type: MonitoringEventType.ACTIVITY_RESUMED,
          timestamp: Date.now(),
          sessionId,
          candidateId,
        });
      }

      if (keyboardTimerRef.current) {
        clearTimeout(keyboardTimerRef.current);
      }
      keyboardTimerRef.current = setTimeout(checkKeyboardInactivity, inactivityThreshold);
    };

    const handleMouseActivity = () => {
      const wasInactive = mouseInactiveRef.current;
      lastMouseActivityRef.current = Date.now();
      mouseInactiveRef.current = false;

      if (wasInactive) {
        monitoringEventEmitter.emit({
          type: MonitoringEventType.ACTIVITY_RESUMED,
          timestamp: Date.now(),
          sessionId,
          candidateId,
        });
      }

      if (mouseTimerRef.current) {
        clearTimeout(mouseTimerRef.current);
      }
      mouseTimerRef.current = setTimeout(checkMouseInactivity, inactivityThreshold);
    };

    document.addEventListener('keydown', handleKeyboardActivity);
    document.addEventListener('keyup', handleKeyboardActivity);
    document.addEventListener('mousemove', handleMouseActivity);
    document.addEventListener('click', handleMouseActivity);

    keyboardTimerRef.current = setTimeout(checkKeyboardInactivity, inactivityThreshold);
    mouseTimerRef.current = setTimeout(checkMouseInactivity, inactivityThreshold);

    return () => {
      document.removeEventListener('keydown', handleKeyboardActivity);
      document.removeEventListener('keyup', handleKeyboardActivity);
      document.removeEventListener('mousemove', handleMouseActivity);
      document.removeEventListener('click', handleMouseActivity);

      if (keyboardTimerRef.current) {
        clearTimeout(keyboardTimerRef.current);
      }
      if (mouseTimerRef.current) {
        clearTimeout(mouseTimerRef.current);
      }
    };
  }, [enabled, inactivityThreshold, sessionId, candidateId]);

  return null;
};
