import { useState, useEffect, useRef, useCallback } from 'react';
import { WebRTCManager, MediaCaptureOptions } from '@/lib/webrtc';

export interface UseWebRTCOptions extends MediaCaptureOptions {
  autoStart?: boolean;
}

export function useWebRTC(options: UseWebRTCOptions = {}) {
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [permissionStatus, setPermissionStatus] = useState<PermissionState>('prompt');
  const [isLoading, setIsLoading] = useState(false);
  const [hasVideo, setHasVideo] = useState(false);
  const [hasAudio, setHasAudio] = useState(false);

  const managerRef = useRef<WebRTCManager | null>(null);

  useEffect(() => {
    managerRef.current = new WebRTCManager();

    if (options.autoStart) {
      startCapture();
    }

    return () => {
      if (managerRef.current) {
        managerRef.current.stopAllTracks();
      }
    };
  }, []);

  const startCapture = useCallback(async () => {
    if (!managerRef.current) {
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const mediaStream = await managerRef.current.requestPermissions(options);
      setStream(mediaStream);
      setPermissionStatus(managerRef.current.getPermissionStatus());
      setHasVideo(managerRef.current.hasVideo());
      setHasAudio(managerRef.current.hasAudio());
    } catch (err) {
      setError(err as Error);
      setPermissionStatus('denied');
    } finally {
      setIsLoading(false);
    }
  }, [options]);

  const retryCapture = useCallback(async (maxRetries: number = 3) => {
    if (!managerRef.current) {
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const mediaStream = await managerRef.current.retryPermissionRequest(options, maxRetries);
      setStream(mediaStream);
      setPermissionStatus(managerRef.current.getPermissionStatus());
      setHasVideo(managerRef.current.hasVideo());
      setHasAudio(managerRef.current.hasAudio());
    } catch (err) {
      setError(err as Error);
      setPermissionStatus('denied');
    } finally {
      setIsLoading(false);
    }
  }, [options]);

  const stopCapture = useCallback(() => {
    if (managerRef.current) {
      managerRef.current.stopAllTracks();
      setStream(null);
      setHasVideo(false);
      setHasAudio(false);
    }
  }, []);

  const toggleVideo = useCallback((enabled: boolean) => {
    if (managerRef.current) {
      managerRef.current.toggleVideo(enabled);
      setHasVideo(managerRef.current.hasVideo());
    }
  }, []);

  const toggleAudio = useCallback((enabled: boolean) => {
    if (managerRef.current) {
      managerRef.current.toggleAudio(enabled);
      setHasAudio(managerRef.current.hasAudio());
    }
  }, []);

  const captureFrame = useCallback((canvas?: HTMLCanvasElement): string | null => {
    if (!managerRef.current) {
      return null;
    }
    return managerRef.current.captureVideoFrame(canvas);
  }, []);

  const attachToVideo = useCallback((videoElement: HTMLVideoElement) => {
    if (managerRef.current && stream) {
      managerRef.current.attachToVideoElement(videoElement);
    }
  }, [stream]);

  return {
    stream,
    error,
    permissionStatus,
    isLoading,
    hasVideo,
    hasAudio,
    startCapture,
    retryCapture,
    stopCapture,
    toggleVideo,
    toggleAudio,
    captureFrame,
    attachToVideo,
    manager: managerRef.current
  };
}
