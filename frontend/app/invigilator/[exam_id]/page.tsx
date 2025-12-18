'use client';

import { useParams, useSearchParams } from 'next/navigation';
import { useEffect, useState } from 'react';
import { useWebSocket } from '@/hooks/useWebSocket';
import { createWebSocketURL } from '@/lib/websocket';
import ConnectionStatus from '@/components/ConnectionStatus';

interface CandidateStatus {
  session_id: string;
  status: string;
  has_video: boolean;
  has_audio: boolean;
  network_quality?: string;
  last_frame?: string;
  last_update?: string;
}

export default function InvigilatorPage() {
  const params = useParams();
  const searchParams = useSearchParams();
  
  const examId = params.exam_id as string;
  const invigilatorId = searchParams.get('invigilator_id') || 'inv-default';

  const [candidates, setCandidates] = useState<Map<string, CandidateStatus>>(new Map());
  const [alerts, setAlerts] = useState<Array<{ timestamp: string; message: string; level: string }>>([]);

  const wsURL = createWebSocketURL(
    `/ws/exam/${examId}?invigilator_id=${invigilatorId}`,
    process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'
  );

  const { connectionState, on } = useWebSocket({ url: wsURL, autoConnect: true });

  useEffect(() => {
    const unsubscribeStatus = on('candidate_status', (data) => {
      setCandidates(prev => {
        const updated = new Map(prev);
        updated.set(data.session_id, {
          ...data,
          last_update: new Date().toISOString()
        });
        return updated;
      });
    });

    const unsubscribeAlert = on('alert', (data) => {
      setAlerts(prev => [{
        timestamp: new Date().toISOString(),
        message: data.message,
        level: data.level
      }, ...prev].slice(0, 20));
    });

    const unsubscribeVideoFrame = on('video_frame', (data) => {
      setCandidates(prev => {
        const updated = new Map(prev);
        const candidate = updated.get(data.session_id);
        if (candidate) {
          updated.set(data.session_id, {
            ...candidate,
            last_frame: data.frame_data,
            last_update: new Date().toISOString()
          });
        } else {
          updated.set(data.session_id, {
            session_id: data.session_id,
            status: 'streaming',
            has_video: true,
            has_audio: false,
            last_frame: data.frame_data,
            last_update: new Date().toISOString()
          });
        }
        return updated;
      });
    });

    return () => {
      unsubscribeStatus();
      unsubscribeAlert();
      unsubscribeVideoFrame();
    };
  }, [on]);

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f8f9fa' }}>
      <header style={{
        backgroundColor: 'white',
        borderBottom: '1px solid #e0e0e0',
        padding: '16px 24px',
        boxShadow: '0 2px 4px rgba(0, 0, 0, 0.05)'
      }}>
        <div style={{
          maxWidth: '1400px',
          margin: '0 auto',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div>
            <h1 style={{
              fontSize: '20px',
              fontWeight: 'bold',
              color: '#1a1a1a',
              marginBottom: '4px'
            }}>
              Online Exam Proctoring - Invigilator
            </h1>
            <p style={{
              fontSize: '14px',
              color: '#4a4a4a'
            }}>
              Exam ID: {examId} | Invigilator: {invigilatorId}
            </p>
          </div>
          <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
            <ConnectionStatus state={connectionState} />
            <a
              href="/"
              style={{
                fontSize: '14px',
                color: '#0066cc',
                textDecoration: 'none'
              }}
            >
              ← Back to Home
            </a>
          </div>
        </div>
      </header>

      <main style={{
        maxWidth: '1400px',
        margin: '0 auto',
        padding: '24px',
        display: 'grid',
        gridTemplateColumns: '1fr 350px',
        gap: '24px'
      }}>
        <div>
          <div style={{
            backgroundColor: 'white',
            borderRadius: '12px',
            padding: '24px',
            marginBottom: '24px',
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)'
          }}>
            <h2 style={{
              fontSize: '20px',
              fontWeight: '600',
              marginBottom: '16px',
              color: '#1a1a1a'
            }}>
              Active Candidates ({candidates.size})
            </h2>
            
            {candidates.size === 0 ? (
              <div style={{
                padding: '40px',
                textAlign: 'center',
                color: '#888',
                backgroundColor: '#f5f5f5',
                borderRadius: '8px'
              }}>
                No candidates connected yet
              </div>
            ) : (
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
                gap: '16px'
              }}>
                {Array.from(candidates.values()).map(candidate => (
                  <div
                    key={candidate.session_id}
                    style={{
                      backgroundColor: '#f8f9fa',
                      borderRadius: '8px',
                      padding: '16px',
                      border: '1px solid #e0e0e0'
                    }}
                  >
                    {candidate.last_frame && (
                      <div style={{
                        marginBottom: '12px',
                        borderRadius: '8px',
                        overflow: 'hidden',
                        backgroundColor: '#000'
                      }}>
                        <img
                          src={candidate.last_frame}
                          alt={`Candidate ${candidate.session_id}`}
                          style={{
                            width: '100%',
                            height: 'auto',
                            display: 'block'
                          }}
                        />
                      </div>
                    )}
                    <div style={{ fontSize: '14px', color: '#4a4a4a' }}>
                      <div style={{ marginBottom: '8px' }}>
                        <strong>Session:</strong> {candidate.session_id}
                      </div>
                      <div style={{ marginBottom: '8px' }}>
                        <strong>Status:</strong>{' '}
                        <span style={{
                          padding: '2px 8px',
                          borderRadius: '4px',
                          backgroundColor: candidate.status === 'streaming' ? '#d4edda' : '#fff3cd',
                          color: candidate.status === 'streaming' ? '#155724' : '#856404'
                        }}>
                          {candidate.status}
                        </span>
                      </div>
                      <div style={{ marginBottom: '8px' }}>
                        <strong>Video:</strong> {candidate.has_video ? '✓ Active' : '✕ Inactive'}
                      </div>
                      <div style={{ marginBottom: '8px' }}>
                        <strong>Audio:</strong> {candidate.has_audio ? '✓ Active' : '✕ Inactive'}
                      </div>
                      {candidate.network_quality && (
                        <div>
                          <strong>Network:</strong> {candidate.network_quality}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        <div>
          <div style={{
            backgroundColor: 'white',
            borderRadius: '12px',
            padding: '24px',
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
            position: 'sticky',
            top: '24px'
          }}>
            <h2 style={{
              fontSize: '20px',
              fontWeight: '600',
              marginBottom: '16px',
              color: '#1a1a1a'
            }}>
              Alerts
            </h2>
            
            {alerts.length === 0 ? (
              <div style={{
                padding: '20px',
                textAlign: 'center',
                color: '#888',
                backgroundColor: '#f5f5f5',
                borderRadius: '8px',
                fontSize: '14px'
              }}>
                No alerts yet
              </div>
            ) : (
              <div style={{
                maxHeight: '600px',
                overflowY: 'auto'
              }}>
                {alerts.map((alert, index) => (
                  <div
                    key={index}
                    style={{
                      padding: '12px',
                      marginBottom: '8px',
                      borderRadius: '6px',
                      backgroundColor: alert.level === 'critical' ? '#f8d7da' :
                                     alert.level === 'warning' ? '#fff3cd' : '#d1ecf1',
                      border: `1px solid ${alert.level === 'critical' ? '#f5c6cb' :
                                          alert.level === 'warning' ? '#ffeeba' : '#bee5eb'}`,
                      fontSize: '14px'
                    }}
                  >
                    <div style={{
                      fontWeight: '600',
                      marginBottom: '4px',
                      color: alert.level === 'critical' ? '#721c24' :
                             alert.level === 'warning' ? '#856404' : '#0c5460'
                    }}>
                      {alert.level.toUpperCase()}
                    </div>
                    <div style={{
                      color: alert.level === 'critical' ? '#721c24' :
                             alert.level === 'warning' ? '#856404' : '#0c5460',
                      marginBottom: '4px'
                    }}>
                      {alert.message}
                    </div>
                    <div style={{
                      fontSize: '12px',
                      color: '#666'
                    }}>
                      {new Date(alert.timestamp).toLocaleTimeString()}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
