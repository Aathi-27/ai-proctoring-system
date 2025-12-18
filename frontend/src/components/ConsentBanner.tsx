import { useState } from 'react';

interface ConsentBannerProps {
  onAccept: () => void;
  onDecline: () => void;
  disablePaste: boolean;
}

export const ConsentBanner: React.FC<ConsentBannerProps> = ({
  onAccept,
  onDecline,
  disablePaste,
}) => {
  const [isVisible, setIsVisible] = useState(true);

  if (!isVisible) {
    return null;
  }

  const handleAccept = () => {
    setIsVisible(false);
    onAccept();
  };

  const handleDecline = () => {
    setIsVisible(false);
    onDecline();
  };

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        backgroundColor: '#1a1a1a',
        color: '#ffffff',
        padding: '20px',
        zIndex: 10000,
        boxShadow: '0 2px 10px rgba(0,0,0,0.3)',
      }}
    >
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <h2 style={{ marginTop: 0, marginBottom: '15px', fontSize: '20px' }}>
          Exam Monitoring Consent
        </h2>
        <div style={{ marginBottom: '20px', lineHeight: '1.6' }}>
          <p style={{ marginBottom: '10px' }}>
            This exam uses activity monitoring to ensure exam integrity. By proceeding, you consent to:
          </p>
          <ul style={{ marginLeft: '20px', marginBottom: '10px' }}>
            <li>
              <strong>Tab/Window Switching Detection:</strong> We track when you switch away from the exam tab
            </li>
            <li>
              <strong>Copy/Paste Detection:</strong> We log copy and paste events (but NOT the actual content)
            </li>
            <li>
              <strong>Inactivity Tracking:</strong> We detect when there is no keyboard or mouse activity for extended periods
            </li>
            {disablePaste && (
              <li>
                <strong>Paste Disabled:</strong> Pasting content is disabled for this exam
              </li>
            )}
          </ul>
          <p style={{ marginBottom: '10px' }}>
            <strong>Privacy:</strong> We do NOT capture clipboard content, keystrokes, or screenshots. 
            Only event occurrences and metadata are logged.
          </p>
          <p style={{ marginBottom: 0 }}>
            <strong>Note:</strong> Declining consent will prevent you from taking this exam.
          </p>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button
            onClick={handleAccept}
            style={{
              backgroundColor: '#4CAF50',
              color: 'white',
              padding: '12px 24px',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '16px',
              fontWeight: 'bold',
            }}
          >
            I Accept - Start Exam
          </button>
          <button
            onClick={handleDecline}
            style={{
              backgroundColor: '#f44336',
              color: 'white',
              padding: '12px 24px',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '16px',
            }}
          >
            I Decline
          </button>
        </div>
      </div>
    </div>
  );
};
