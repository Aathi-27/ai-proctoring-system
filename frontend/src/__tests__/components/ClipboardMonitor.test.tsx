import { render, waitFor } from '@testing-library/react';
import { ClipboardMonitor } from '../../components/monitoring/ClipboardMonitor';
import { monitoringEventEmitter } from '../../lib/eventEmitter';
import { MonitoringEventType } from '../../types/monitoring';

describe('ClipboardMonitor', () => {
  let emitSpy: jest.SpyInstance;

  beforeEach(() => {
    emitSpy = jest.spyOn(monitoringEventEmitter, 'emit');
  });

  afterEach(() => {
    emitSpy.mockRestore();
  });

  it('should not emit events when disabled', () => {
    render(
      <ClipboardMonitor
        enabled={false}
        disablePaste={false}
        sessionId="test-session"
        candidateId="test-candidate"
      />
    );

    const copyEvent = new ClipboardEvent('copy');
    document.dispatchEvent(copyEvent);

    expect(emitSpy).not.toHaveBeenCalled();
  });

  it('should emit COPY_DETECTED event on copy', async () => {
    render(
      <ClipboardMonitor
        enabled={true}
        disablePaste={false}
        sessionId="test-session"
        candidateId="test-candidate"
      />
    );

    window.getSelection = jest.fn().mockReturnValue({
      toString: () => 'test content',
    });

    const copyEvent = new ClipboardEvent('copy');
    document.dispatchEvent(copyEvent);

    await waitFor(() => {
      expect(emitSpy).toHaveBeenCalledWith(
        expect.objectContaining({
          type: MonitoringEventType.COPY_DETECTED,
          sessionId: 'test-session',
          candidateId: 'test-candidate',
          content_length: expect.any(Number),
        })
      );
    });
  });

  it('should emit PASTE_DETECTED event on paste', async () => {
    render(
      <ClipboardMonitor
        enabled={true}
        disablePaste={false}
        sessionId="test-session"
        candidateId="test-candidate"
      />
    );

    const pasteEvent = new ClipboardEvent('paste', {
      clipboardData: new DataTransfer(),
    });

    Object.defineProperty(pasteEvent, 'clipboardData', {
      value: {
        getData: () => 'pasted content',
      },
    });

    document.dispatchEvent(pasteEvent);

    await waitFor(() => {
      expect(emitSpy).toHaveBeenCalledWith(
        expect.objectContaining({
          type: MonitoringEventType.PASTE_DETECTED,
          sessionId: 'test-session',
          candidateId: 'test-candidate',
          content_length: expect.any(Number),
        })
      );
    });
  });

  it('should prevent paste when disablePaste is true', async () => {
    render(
      <ClipboardMonitor
        enabled={true}
        disablePaste={true}
        sessionId="test-session"
        candidateId="test-candidate"
      />
    );

    const pasteEvent = new ClipboardEvent('paste', {
      clipboardData: new DataTransfer(),
      cancelable: true,
    });

    Object.defineProperty(pasteEvent, 'clipboardData', {
      value: {
        getData: () => 'pasted content',
      },
    });

    const preventDefaultSpy = jest.spyOn(pasteEvent, 'preventDefault');
    document.dispatchEvent(pasteEvent);

    await waitFor(() => {
      expect(preventDefaultSpy).toHaveBeenCalled();
    });
  });

  it('should emit COPY_DETECTED on cut event', async () => {
    render(
      <ClipboardMonitor
        enabled={true}
        disablePaste={false}
        sessionId="test-session"
        candidateId="test-candidate"
      />
    );

    window.getSelection = jest.fn().mockReturnValue({
      toString: () => 'cut content',
    });

    const cutEvent = new ClipboardEvent('cut');
    document.dispatchEvent(cutEvent);

    await waitFor(() => {
      expect(emitSpy).toHaveBeenCalledWith(
        expect.objectContaining({
          type: MonitoringEventType.COPY_DETECTED,
          sessionId: 'test-session',
          candidateId: 'test-candidate',
        })
      );
    });
  });
});
