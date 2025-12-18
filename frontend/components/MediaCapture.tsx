'use client';

import { useState, useEffect, useRef } from 'react';
import { useWebRTC } from '@/hooks/useWebRTC';
import { useWebSocket } from '@/hooks/useWebSocket';
import { createWebSocketURL } from '@/lib/websocket';
import ConsentBanner from './ConsentBanner';
import VideoPreview from './VideoPreview';
import AudioLevelVisualizer from './AudioLevelVisualizer';
import ConnectionStatus from './ConnectionStatus';

export interface MediaCaptureProps {
  sessionId: string;
  examId?: string;
  wsBaseURL?: string;
  videoQuality?: 'low' | 'medium' | 'high';
  fps?: number;
  onPermissionGranted?: () => void;
  onPermissionDenied?: () => void;
  onError?: (error: Error) => void;
}

export default function MediaCapture({
  sessionId,
  examId,
  wsBaseURL = 'ws://localhost:8000',
  videoQuality = 'medium',
  fps = 10,
  onPermissionGranted,
  onPermissionDenied,
  onError
}: MediaCaptureProps) {
  const [consentGiven, setConsentGiven] = useState(false);
  const [frameNumber, setFrameNumber] = useState(0);
  const frameIntervalRef = useRef<NodeJS.Timeout | null>(null);

  const wsURL = createWebSocketURL(
    `/ws/candidate/${sessionId}${examId ? `?exam_id=${examId}` : ''}`,
    wsBaseURL
  );

  const {
    stream,
    error: webrtcError,
    permissionStatus,
    isLoading,
    hasVideo,
    hasAudio,
    startCapture,
    stopCapture,
    captureFrame,
    toggleVideo,
    toggleAudio
  } = useWebRTC({ videoQuality, fps });

  const {
    connectionState,
    isConnected,
    sendVideoFrame,
    sendCandidateStatus,
    sendPermissionGranted,
    sendPermissionDenied,
    on
  } = useWebSocket({ url: wsURL, autoConnect: true });

  useEffect(() => {
    if (webrtcError && onError) {
      onError(webrtcError);
    }
  }, [webrtcError, onError]);

  useEffect(() => {
    if (permissionStatus === 'granted' && onPermissionGranted) {
      onPermissionGranted();
      sendPermissionGranted();
    } else if (permissionStatus === 'denied' && onPermissionDenied) {
      onPermissionDenied();
      sendPermissionDenied(webrtcError?.message);
    }
  }, [permissionStatus]);

  useEffect(() => {
    if (isConnected && stream) {
      sendCandidateStatus(sessionId, 'streaming', hasVideo, hasAudio, 'good');
    }
  }, [isConnected, stream, hasVideo, hasAudio]);

  useEffect(() => {
    if (stream && isConnected && hasVideo) {
      const interval = 1000 / fps;
      
      frameIntervalRef.current = setInterval(() => {
        const frameData = captureFrame();
        if (frameData) {
          sendVideoFrame(sessionId, frameData, frameNumber, videoQuality);
          setFrameNumber(prev => prev + 1);
        }
      }, interval);

      return () => {
        if (frameIntervalRef.current) {
          clearInterval(frameIntervalRef.current);
        }
      };
    }
  }, [stream, isConnected, hasVideo, fps, frameNumber]);

  useEffect(() => {
    const unsubscribe = on('alert', (data) => {
      console.log('Received alert:', data);
    });

    return () => {
      unsubscribe();
    };
  }, [on]);

  const handleConsentAccept = async () => {
    setConsentGiven(true);
    try {
      await startCapture();
    } catch (err) {
      console.error('Failed to start capture:', err);
    }
  };

  const handleConsentDecline = () => {
    setConsentGiven(false);
    if (onPermissionDenied) {
      onPermissionDenied();
    }
    sendPermissionDenied('User declined consent');
  };

  if (!consentGiven) {
    return (
      <ConsentBanner
        onAccept={handleConsentAccept}
        onDecline={handleConsentDecline}
      />
    );
  }

  return (
    <div style={{
      maxWidth: '900px',
      margin: '0 auto',
      padding: '24px'
    }}>
      <div style={{
        marginBottom: '24px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <h2 style={{
          fontSize: '24px',
          fontWeight: 'bold',
          color: '#1a1a1a'
        }}>
          Exam Session
        </h2>
        <ConnectionStatus state={connectionState} />
      </div>

      {isLoading && (
        <div style={{
          padding: '40px',
          textAlign: 'center',
          backgroundColor: '#f5f5f5',
          borderRadius: '8px',
          marginBottom: '24px'
        }}>
          <p style={{ fontSize: '16px', color: '#4a4a4a' }}>
            Requesting camera and microphone access...
          </p>
        </div>
      )}

      {webrtcError && (
        <div style={{
          padding: '16px',
          backgroundColor: '#fff3cd',
          border: '1px solid #ffc107',
          borderRadius: '8px',
          marginBottom: '24px',
          color: '#856404'
        }}>
          <strong>Error:</strong> {webrtcError.message}
        </div>
      )}

      {stream && (
        <>
          <div style={{
            marginBottom: '24px',
            backgroundColor: '#f5f5f5',
            borderRadius: '8px',
            padding: '16px'
          }}>
            <h3 style={{
              fontSize: '16px',
              fontWeight: '600',
              marginBottom: '12px',
              color: '#1a1a1a'
            }}>
              Video Preview
            </h3>
            <VideoPreview stream={stream} />
            <div style={{
              marginTop: '12px',
              display: 'flex',
              gap: '8px'
            }}>
              <button
                onClick={() => toggleVideo(!hasVideo)}
                style={{
                  padding: '8px 16px',
                  fontSize: '14px',
                  borderRadius: '6px',
                  border: 'none',
                  backgroundColor: hasVideo ? '#dc3545' : '#28a745',
                  color: 'white',
                  cursor: 'pointer'
                }}
              >
                {hasVideo ? 'Disable Video' : 'Enable Video'}
              </button>
              <button
                onClick={() => toggleAudio(!hasAudio)}
                style={{
                  padding: '8px 16px',
                  fontSize: '14px',
                  borderRadius: '6px',
                  border: 'none',
                  backgroundColor: hasAudio ? '#dc3545' : '#28a745',
                  color: 'white',
                  cursor: 'pointer'
                }}
              >
                {hasAudio ? 'Mute Audio' : 'Unmute Audio'}
              </button>
            </div>
          </div>

          <div style={{
            backgroundColor: '#f5f5f5',
            borderRadius: '8px',
            padding: '16px',
            marginBottom: '24px'
          }}>
            <h3 style={{
              fontSize: '16px',
              fontWeight: '600',
              marginBottom: '12px',
              color: '#1a1a1a'
            }}>
              Audio Level
            </h3>
            <AudioLevelVisualizer stream={stream} />
          </div>

          <div style={{
            backgroundColor: '#e8f4fd',
            borderRadius: '8px',
            padding: '16px'
          }}>
            <h3 style={{
              fontSize: '16px',
              fontWeight: '600',
              marginBottom: '12px',
              color: '#1a1a1a'
            }}>
              Session Information
            </h3>
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(2, 1fr)',
              gap: '12px',
              fontSize: '14px',
              color: '#4a4a4a'
            }}>
              <div>
                <strong>Session ID:</strong> {sessionId}
              </div>
              {examId && (
                <div>
                  <strong>Exam ID:</strong> {examId}
                </div>
              )}
              <div>
                <strong>Video:</strong> {hasVideo ? 'Active' : 'Inactive'}
              </div>
              <div>
                <strong>Audio:</strong> {hasAudio ? 'Active' : 'Inactive'}
              </div>
              <div>
                <strong>Quality:</strong> {videoQuality}
              </div>
              <div>
                <strong>FPS:</strong> {fps}
              </div>
              <div>
                <strong>Frames Sent:</strong> {frameNumber}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
