import { render, waitFor } from '@testing-library/react';
import { InactivityTracker } from '../../components/monitoring/InactivityTracker';
import { monitoringEventEmitter } from '../../lib/eventEmitter';
import { MonitoringEventType } from '../../types/monitoring';

describe('InactivityTracker', () => {
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
      <InactivityTracker
        enabled={false}
        inactivityThreshold={30000}
        sessionId="test-session"
        candidateId="test-candidate"
      />
    );

    jest.advanceTimersByTime(35000);

    expect(emitSpy).not.toHaveBeenCalled();
  });

  it('should emit KEYBOARD_INACTIVITY after threshold', async () => {
    render(
      <InactivityTracker
        enabled={true}
        inactivityThreshold={30000}
        sessionId="test-session"
        candidateId="test-candidate"
      />
    );

    jest.advanceTimersByTime(31000);

    await waitFor(() => {
      expect(emitSpy).toHaveBeenCalledWith(
        expect.objectContaining({
          type: MonitoringEventType.KEYBOARD_INACTIVITY,
          sessionId: 'test-session',
          candidateId: 'test-candidate',
          duration_seconds: expect.any(Number),
        })
      );
    });
  });

  it('should emit MOUSE_INACTIVITY after threshold', async () => {
    render(
      <InactivityTracker
        enabled={true}
        inactivityThreshold={30000}
        sessionId="test-session"
        candidateId="test-candidate"
      />
    );

    jest.advanceTimersByTime(31000);

    await waitFor(() => {
      expect(emitSpy).toHaveBeenCalledWith(
        expect.objectContaining({
          type: MonitoringEventType.MOUSE_INACTIVITY,
          sessionId: 'test-session',
          candidateId: 'test-candidate',
        })
      );
    });
  });

  it('should reset timer on keyboard activity', async () => {
    render(
      <InactivityTracker
        enabled={true}
        inactivityThreshold={30000}
        sessionId="test-session"
        candidateId="test-candidate"
      />
    );

    jest.advanceTimersByTime(20000);
    document.dispatchEvent(new KeyboardEvent('keydown'));
    jest.advanceTimersByTime(20000);

    const inactivityCalls = emitSpy.mock.calls.filter(
      call => call[0].type === MonitoringEventType.KEYBOARD_INACTIVITY
    );

    expect(inactivityCalls.length).toBe(0);
  });

  it('should emit ACTIVITY_RESUMED when activity resumes after inactivity', async () => {
    render(
      <InactivityTracker
        enabled={true}
        inactivityThreshold={30000}
        sessionId="test-session"
        candidateId="test-candidate"
      />
    );

    jest.advanceTimersByTime(31000);

    await waitFor(() => {
      expect(emitSpy).toHaveBeenCalledWith(
        expect.objectContaining({
          type: MonitoringEventType.KEYBOARD_INACTIVITY,
        })
      );
    });

    emitSpy.mockClear();

    document.dispatchEvent(new KeyboardEvent('keydown'));

    await waitFor(() => {
      expect(emitSpy).toHaveBeenCalledWith(
        expect.objectContaining({
          type: MonitoringEventType.ACTIVITY_RESUMED,
          sessionId: 'test-session',
          candidateId: 'test-candidate',
        })
      );
    });
  });

  it('should track mouse activity independently', async () => {
    render(
      <InactivityTracker
        enabled={true}
        inactivityThreshold={30000}
        sessionId="test-session"
        candidateId="test-candidate"
      />
    );

    jest.advanceTimersByTime(20000);
    document.dispatchEvent(new MouseEvent('mousemove'));
    jest.advanceTimersByTime(20000);

    const inactivityCalls = emitSpy.mock.calls.filter(
      call => call[0].type === MonitoringEventType.MOUSE_INACTIVITY
    );

    expect(inactivityCalls.length).toBe(0);
  });
});
