import { monitoringEventEmitter } from '../../lib/eventEmitter';
import { MonitoringEventType } from '../../types/monitoring';

describe('EventEmitter', () => {
  beforeEach(() => {
    monitoringEventEmitter.clear();
  });

  it('should subscribe and receive events', () => {
    const callback = jest.fn();
    monitoringEventEmitter.subscribe(callback);

    const event = {
      type: MonitoringEventType.TAB_SWITCHED,
      timestamp: Date.now(),
      inactive_duration: 5000,
      sessionId: 'test-session',
      candidateId: 'test-candidate',
    };

    monitoringEventEmitter.emit(event);

    expect(callback).toHaveBeenCalledWith(event);
    expect(callback).toHaveBeenCalledTimes(1);
  });

  it('should unsubscribe listeners', () => {
    const callback = jest.fn();
    const unsubscribe = monitoringEventEmitter.subscribe(callback);

    const event = {
      type: MonitoringEventType.COPY_DETECTED,
      timestamp: Date.now(),
      content_length: 100,
      sessionId: 'test-session',
      candidateId: 'test-candidate',
    };

    monitoringEventEmitter.emit(event);
    expect(callback).toHaveBeenCalledTimes(1);

    unsubscribe();
    monitoringEventEmitter.emit(event);
    expect(callback).toHaveBeenCalledTimes(1);
  });

  it('should handle multiple subscribers', () => {
    const callback1 = jest.fn();
    const callback2 = jest.fn();

    monitoringEventEmitter.subscribe(callback1);
    monitoringEventEmitter.subscribe(callback2);

    const event = {
      type: MonitoringEventType.KEYBOARD_INACTIVITY,
      timestamp: Date.now(),
      duration_seconds: 30,
      sessionId: 'test-session',
      candidateId: 'test-candidate',
    };

    monitoringEventEmitter.emit(event);

    expect(callback1).toHaveBeenCalledWith(event);
    expect(callback2).toHaveBeenCalledWith(event);
  });

  it('should handle errors in listeners without breaking other listeners', () => {
    const errorCallback = jest.fn(() => {
      throw new Error('Test error');
    });
    const goodCallback = jest.fn();

    monitoringEventEmitter.subscribe(errorCallback);
    monitoringEventEmitter.subscribe(goodCallback);

    const event = {
      type: MonitoringEventType.PASTE_DETECTED,
      timestamp: Date.now(),
      content_length: 50,
      sessionId: 'test-session',
      candidateId: 'test-candidate',
    };

    const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation();

    monitoringEventEmitter.emit(event);

    expect(errorCallback).toHaveBeenCalled();
    expect(goodCallback).toHaveBeenCalled();
    expect(consoleErrorSpy).toHaveBeenCalled();

    consoleErrorSpy.mockRestore();
  });

  it('should clear all listeners', () => {
    const callback1 = jest.fn();
    const callback2 = jest.fn();

    monitoringEventEmitter.subscribe(callback1);
    monitoringEventEmitter.subscribe(callback2);

    monitoringEventEmitter.clear();

    const event = {
      type: MonitoringEventType.TAB_SWITCHED,
      timestamp: Date.now(),
      inactive_duration: 1000,
      sessionId: 'test-session',
      candidateId: 'test-candidate',
    };

    monitoringEventEmitter.emit(event);

    expect(callback1).not.toHaveBeenCalled();
    expect(callback2).not.toHaveBeenCalled();
  });
});
