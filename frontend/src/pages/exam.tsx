import { useState } from 'react';
import { ActivityMonitor } from '../components/monitoring/ActivityMonitor';
import { ConsentBanner } from '../components/ConsentBanner';
import { MonitoringConfig } from '../types/monitoring';

const ExamPage = () => {
  const [consentGiven, setConsentGiven] = useState(false);
  const [monitoringEnabled, setMonitoringEnabled] = useState(false);

  const monitoringConfig: MonitoringConfig = {
    sessionId: `session-${Date.now()}`,
    candidateId: 'candidate-123',
    inactivityThreshold: 30000,
    disablePaste: true,
    websocketUrl: process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws',
  };

  const handleAcceptConsent = () => {
    setConsentGiven(true);
    setMonitoringEnabled(true);
  };

  const handleDeclineConsent = () => {
    setConsentGiven(false);
    alert('You must accept monitoring to take the exam.');
  };

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f5f5f5' }}>
      {!consentGiven && (
        <ConsentBanner
          onAccept={handleAcceptConsent}
          onDecline={handleDeclineConsent}
          disablePaste={monitoringConfig.disablePaste}
        />
      )}

      <ActivityMonitor config={monitoringConfig} enabled={monitoringEnabled} />

      {consentGiven && (
        <div style={{ padding: '40px', maxWidth: '1200px', margin: '0 auto' }}>
          <header style={{ marginBottom: '30px' }}>
            <h1 style={{ fontSize: '32px', marginBottom: '10px' }}>
              Sample Online Exam
            </h1>
            <p style={{ color: '#666' }}>
              Activity monitoring is active. Do not switch tabs or copy/paste content.
            </p>
          </header>

          <div style={{ backgroundColor: 'white', padding: '30px', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
            <h2 style={{ marginBottom: '20px' }}>Question 1</h2>
            <p style={{ marginBottom: '20px', lineHeight: '1.6' }}>
              What is the capital of France?
            </p>
            <div style={{ marginBottom: '30px' }}>
              <label style={{ display: 'block', marginBottom: '10px' }}>
                <input type="radio" name="q1" value="a" style={{ marginRight: '10px' }} />
                A) London
              </label>
              <label style={{ display: 'block', marginBottom: '10px' }}>
                <input type="radio" name="q1" value="b" style={{ marginRight: '10px' }} />
                B) Paris
              </label>
              <label style={{ display: 'block', marginBottom: '10px' }}>
                <input type="radio" name="q1" value="c" style={{ marginRight: '10px' }} />
                C) Berlin
              </label>
              <label style={{ display: 'block', marginBottom: '10px' }}>
                <input type="radio" name="q1" value="d" style={{ marginRight: '10px' }} />
                D) Madrid
              </label>
            </div>

            <h2 style={{ marginBottom: '20px' }}>Question 2</h2>
            <p style={{ marginBottom: '20px', lineHeight: '1.6' }}>
              Explain the concept of closure in JavaScript.
            </p>
            <textarea
              style={{
                width: '100%',
                minHeight: '150px',
                padding: '10px',
                fontSize: '14px',
                borderRadius: '4px',
                border: '1px solid #ddd',
                fontFamily: 'inherit',
              }}
              placeholder="Type your answer here..."
            />

            <div style={{ marginTop: '30px' }}>
              <button
                style={{
                  backgroundColor: '#2196F3',
                  color: 'white',
                  padding: '12px 30px',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  fontSize: '16px',
                  fontWeight: 'bold',
                }}
              >
                Submit Exam
              </button>
            </div>
          </div>

          <div style={{ marginTop: '30px', padding: '20px', backgroundColor: '#fff3cd', borderRadius: '8px', border: '1px solid #ffc107' }}>
            <h3 style={{ marginTop: 0, marginBottom: '10px' }}>Testing the Monitoring System</h3>
            <ul style={{ marginLeft: '20px', lineHeight: '1.8' }}>
              <li>Try switching to another tab or window - this will be logged</li>
              <li>Try copying text (Ctrl+C / Cmd+C) - this will be logged</li>
              <li>Try pasting (Ctrl+V / Cmd+V) - this will be blocked and logged</li>
              <li>Remain idle for 30+ seconds - inactivity will be detected</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};

export default ExamPage;
