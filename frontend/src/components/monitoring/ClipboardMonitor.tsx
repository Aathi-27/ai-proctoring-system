import { useEffect } from 'react';
import { MonitoringEventType } from '../../types/monitoring';
import { monitoringEventEmitter } from '../../lib/eventEmitter';

interface ClipboardMonitorProps {
  enabled: boolean;
  disablePaste: boolean;
  sessionId: string;
  candidateId: string;
}

export const ClipboardMonitor: React.FC<ClipboardMonitorProps> = ({
  enabled,
  disablePaste,
  sessionId,
  candidateId,
}) => {
  useEffect(() => {
    if (!enabled || typeof window === 'undefined') return;

    const handleCopy = (e: ClipboardEvent) => {
      const selection = window.getSelection();
      const selectedText = selection?.toString() || '';
      
      monitoringEventEmitter.emit({
        type: MonitoringEventType.COPY_DETECTED,
        timestamp: Date.now(),
        content_length: new Blob([selectedText]).size,
        sessionId,
        candidateId,
      });
    };

    const handlePaste = (e: ClipboardEvent) => {
      const clipboardData = e.clipboardData?.getData('text') || '';
      
      monitoringEventEmitter.emit({
        type: MonitoringEventType.PASTE_DETECTED,
        timestamp: Date.now(),
        content_length: new Blob([clipboardData]).size,
        sessionId,
        candidateId,
      });

      if (disablePaste) {
        e.preventDefault();
        console.warn('Paste functionality is disabled for this exam');
      }
    };

    const handleCut = (e: ClipboardEvent) => {
      const selection = window.getSelection();
      const selectedText = selection?.toString() || '';
      
      monitoringEventEmitter.emit({
        type: MonitoringEventType.COPY_DETECTED,
        timestamp: Date.now(),
        content_length: new Blob([selectedText]).size,
        sessionId,
        candidateId,
      });

      if (disablePaste) {
        e.preventDefault();
      }
    };

    document.addEventListener('copy', handleCopy);
    document.addEventListener('paste', handlePaste);
    document.addEventListener('cut', handleCut);

    return () => {
      document.removeEventListener('copy', handleCopy);
      document.removeEventListener('paste', handlePaste);
      document.removeEventListener('cut', handleCut);
    };
  }, [enabled, disablePaste, sessionId, candidateId]);

  return null;
};
