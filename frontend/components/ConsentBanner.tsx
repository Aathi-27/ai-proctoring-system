'use client';

import { useState } from 'react';

export interface ConsentBannerProps {
  onAccept: () => void;
  onDecline: () => void;
}

export default function ConsentBanner({ onAccept, onDecline }: ConsentBannerProps) {
  const [showDetails, setShowDetails] = useState(false);

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 9999,
      padding: '20px'
    }}>
      <div style={{
        backgroundColor: 'white',
        borderRadius: '12px',
        padding: '32px',
        maxWidth: '600px',
        width: '100%',
        boxShadow: '0 20px 60px rgba(0, 0, 0, 0.3)'
      }}>
        <div style={{ marginBottom: '24px' }}>
          <h2 style={{
            fontSize: '24px',
            fontWeight: 'bold',
            marginBottom: '12px',
            color: '#1a1a1a'
          }}>
            Media Access Consent Required
          </h2>
          <p style={{
            fontSize: '16px',
            lineHeight: '1.6',
            color: '#4a4a4a',
            marginBottom: '16px'
          }}>
            To proceed with this exam, we need your permission to access your camera and microphone.
            This is required for exam proctoring and integrity purposes.
          </p>
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
            What we collect:
          </h3>
          <ul style={{
            fontSize: '14px',
            lineHeight: '1.8',
            color: '#4a4a4a',
            paddingLeft: '20px'
          }}>
            <li>Video feed from your webcam during the exam</li>
            <li>Audio from your microphone during the exam</li>
            <li>Real-time monitoring by exam invigilators</li>
          </ul>
        </div>

        {showDetails && (
          <div style={{
            backgroundColor: '#e8f4fd',
            borderRadius: '8px',
            padding: '16px',
            marginBottom: '24px',
            fontSize: '14px',
            lineHeight: '1.6',
            color: '#1a1a1a'
          }}>
            <h3 style={{
              fontSize: '16px',
              fontWeight: '600',
              marginBottom: '12px'
            }}>
              Privacy & Data Handling:
            </h3>
            <ul style={{ paddingLeft: '20px' }}>
              <li>Media streams are transmitted in real-time only</li>
              <li>No permanent recording or storage at this stage (Phase 1)</li>
              <li>Data is processed securely over encrypted connections</li>
              <li>Invigilators monitor only for exam integrity purposes</li>
              <li>You can stop the exam at any time</li>
            </ul>
          </div>
        )}

        <button
          onClick={() => setShowDetails(!showDetails)}
          style={{
            fontSize: '14px',
            color: '#0066cc',
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            marginBottom: '24px',
            textDecoration: 'underline'
          }}
        >
          {showDetails ? 'Hide details' : 'Show more details'}
        </button>

        <div style={{
          display: 'flex',
          gap: '12px',
          justifyContent: 'flex-end'
        }}>
          <button
            onClick={onDecline}
            style={{
              padding: '12px 24px',
              fontSize: '16px',
              fontWeight: '500',
              borderRadius: '8px',
              border: '2px solid #e0e0e0',
              backgroundColor: 'white',
              color: '#4a4a4a',
              cursor: 'pointer',
              transition: 'all 0.2s'
            }}
            onMouseOver={(e) => {
              e.currentTarget.style.backgroundColor = '#f5f5f5';
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.backgroundColor = 'white';
            }}
          >
            Decline
          </button>
          <button
            onClick={onAccept}
            style={{
              padding: '12px 24px',
              fontSize: '16px',
              fontWeight: '500',
              borderRadius: '8px',
              border: 'none',
              backgroundColor: '#0066cc',
              color: 'white',
              cursor: 'pointer',
              transition: 'all 0.2s'
            }}
            onMouseOver={(e) => {
              e.currentTarget.style.backgroundColor = '#0052a3';
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.backgroundColor = '#0066cc';
            }}
          >
            Accept & Continue
          </button>
        </div>

        <p style={{
          fontSize: '12px',
          color: '#888',
          marginTop: '16px',
          textAlign: 'center'
        }}>
          By accepting, you consent to the collection and processing of your media data as described above.
        </p>
      </div>
    </div>
  );
}
