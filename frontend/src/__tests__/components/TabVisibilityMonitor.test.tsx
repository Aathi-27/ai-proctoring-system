import { renderHook, waitFor } from '@testing-library/react';
import { TabVisibilityMonitor } from '../../components/monitoring/TabVisibilityMonitor';
import { monitoringEventEmitter } from '../../lib/eventEmitter';
import { MonitoringEventType } from '../../types/monitoring';
import { render } from '@testing-library/react';

describe('TabVisibilityMonitor', () => {
  let emitSpy: jest.SpyInstance;

  beforeEach(() => {
    emitSpy = jest.spyOn(monitoringEventEmitter, 'emit');
    jest.useFakeTimers();
  });

  afterEach(() => {
    emitSpy.mockRestore();
    jest.useRealTimers();
  });

  it('should not emit events when disabled', () => {
    render(
      <TabVisibilityMonitor
        enabled={false}
        sessionId="test-session"
        candidateId="test-candidate"
      />
    );

    Object.defineProperty(document, 'hidden', {
      configurable: true,
      get: () => true,
    });

    document.dispatchEvent(new Event('visibilitychange'));

    expect(emitSpy).not.toHaveBeenCalled();
  });

  it('should emit TAB_SWITCHED event on visibility change', async () => {
    render(
      <TabVisibilityMonitor
        enabled={true}
        sessionId="test-session"
        candidateId="test-candidate"
      />
    );

    Object.defineProperty(document, 'hidden', {
      configurable: true,
      get: () => true,
    });
    document.dispatchEvent(new Event('visibilitychange'));

    jest.advanceTimersByTime(5000);

    Object.defineProperty(document, 'hidden', {
      configurable: true,
      get: () => false,
    });
    document.dispatchEvent(new Event('visibilitychange'));

    await waitFor(() => {
      expect(emitSpy).toHaveBeenCalledWith(
        expect.objectContaining({
          type: MonitoringEventType.TAB_SWITCHED,
          sessionId: 'test-session',
          candidateId: 'test-candidate',
        })
      );
    });
  });

  it('should emit TAB_SWITCHED event on window blur/focus', async () => {
    render(
      <TabVisibilityMonitor
        enabled={true}
        sessionId="test-session"
        candidateId="test-candidate"
      />
    );

    window.dispatchEvent(new Event('blur'));
    jest.advanceTimersByTime(3000);
    window.dispatchEvent(new Event('focus'));

    await waitFor(() => {
      expect(emitSpy).toHaveBeenCalledWith(
        expect.objectContaining({
          type: MonitoringEventType.TAB_SWITCHED,
          sessionId: 'test-session',
          candidateId: 'test-candidate',
        })
      );
    });
  });

  it('should track inactive duration correctly', async () => {
    render(
      <TabVisibilityMonitor
        enabled={true}
        sessionId="test-session"
        candidateId="test-candidate"
      />
    );

    const startTime = Date.now();
    jest.spyOn(Date, 'now').mockReturnValue(startTime);

    window.dispatchEvent(new Event('blur'));

    const endTime = startTime + 10000;
    jest.spyOn(Date, 'now').mockReturnValue(endTime);

    window.dispatchEvent(new Event('focus'));

    await waitFor(() => {
      expect(emitSpy).toHaveBeenCalledWith(
        expect.objectContaining({
          type: MonitoringEventType.TAB_SWITCHED,
          inactive_duration: 10000,
        })
      );
    });
  });
});
