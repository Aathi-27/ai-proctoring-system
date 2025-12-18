export enum MonitoringEventType {
  TAB_SWITCHED = 'TAB_SWITCHED',
  COPY_DETECTED = 'COPY_DETECTED',
  PASTE_DETECTED = 'PASTE_DETECTED',
  KEYBOARD_INACTIVITY = 'KEYBOARD_INACTIVITY',
  MOUSE_INACTIVITY = 'MOUSE_INACTIVITY',
  ACTIVITY_RESUMED = 'ACTIVITY_RESUMED',
}

export interface BaseMonitoringEvent {
  type: MonitoringEventType;
  timestamp: number;
  sessionId?: string;
  candidateId?: string;
}

export interface TabSwitchedEvent extends BaseMonitoringEvent {
  type: MonitoringEventType.TAB_SWITCHED;
  inactive_duration: number;
}

export interface ClipboardEvent extends BaseMonitoringEvent {
  type: MonitoringEventType.COPY_DETECTED | MonitoringEventType.PASTE_DETECTED;
  content_length: number;
}

export interface InactivityEvent extends BaseMonitoringEvent {
  type: MonitoringEventType.KEYBOARD_INACTIVITY | MonitoringEventType.MOUSE_INACTIVITY;
  duration_seconds: number;
}

export interface ActivityResumedEvent extends BaseMonitoringEvent {
  type: MonitoringEventType.ACTIVITY_RESUMED;
}

export type MonitoringEvent = 
  | TabSwitchedEvent 
  | ClipboardEvent 
  | InactivityEvent 
  | ActivityResumedEvent;

export interface MonitoringConfig {
  sessionId: string;
  candidateId: string;
  inactivityThreshold: number;
  disablePaste: boolean;
  websocketUrl: string;
}
