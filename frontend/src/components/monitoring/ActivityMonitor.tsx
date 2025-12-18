import { useEffect } from 'react';
import { MonitoringConfig } from '../../types/monitoring';
import { monitoringEventEmitter } from '../../lib/eventEmitter';
import { useWebSocket } from '../../hooks/useWebSocket';
import { TabVisibilityMonitor } from './TabVisibilityMonitor';
import { ClipboardMonitor } from './ClipboardMonitor';
import { InactivityTracker } from './InactivityTracker';

interface ActivityMonitorProps {
  config: MonitoringConfig;
  enabled: boolean;
}

export const ActivityMonitor: React.FC<ActivityMonitorProps> = ({ config, enabled }) => {
  const { sendEvent, isConnected } = useWebSocket({
    url: config.websocketUrl,
    enabled,
    onConnect: () => {
      console.log('Monitoring WebSocket connected');
    },
    onDisconnect: () => {
      console.log('Monitoring WebSocket disconnected');
    },
    onError: (error) => {
      console.error('Monitoring WebSocket error:', error);
    },
  });

  useEffect(() => {
    if (!enabled) return;

    const unsubscribe = monitoringEventEmitter.subscribe((event) => {
      console.log('Monitoring event:', event.type, event);
      sendEvent(event);
    });

    return () => {
      unsubscribe();
    };
  }, [enabled, sendEvent]);

  if (!enabled) {
    return null;
  }

  return (
    <>
      <TabVisibilityMonitor
        enabled={enabled}
        sessionId={config.sessionId}
        candidateId={config.candidateId}
      />
      <ClipboardMonitor
        enabled={enabled}
        disablePaste={config.disablePaste}
        sessionId={config.sessionId}
        candidateId={config.candidateId}
      />
      <InactivityTracker
        enabled={enabled}
        inactivityThreshold={config.inactivityThreshold}
        sessionId={config.sessionId}
        candidateId={config.candidateId}
      />
      {isConnected && (
        <div style={{ display: 'none' }} data-testid="monitoring-active" />
      )}
    </>
  );
};
