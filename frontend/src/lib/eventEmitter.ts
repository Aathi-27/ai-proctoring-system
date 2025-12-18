import { MonitoringEvent } from '../types/monitoring';

type EventCallback = (event: MonitoringEvent) => void;

class EventEmitter {
  private listeners: EventCallback[] = [];

  subscribe(callback: EventCallback): () => void {
    this.listeners.push(callback);
    return () => {
      this.listeners = this.listeners.filter(listener => listener !== callback);
    };
  }

  emit(event: MonitoringEvent): void {
    this.listeners.forEach(listener => {
      try {
        listener(event);
      } catch (error) {
        console.error('Error in event listener:', error);
      }
    });
  }

  clear(): void {
    this.listeners = [];
  }
}

export const monitoringEventEmitter = new EventEmitter();
