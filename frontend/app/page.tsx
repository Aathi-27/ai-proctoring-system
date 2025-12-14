import Link from 'next/link'

export default function Home() {
  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '24px',
      backgroundColor: '#f8f9fa'
    }}>
      <div style={{
        maxWidth: '800px',
        width: '100%',
        textAlign: 'center'
      }}>
        <h1 style={{
          fontSize: '48px',
          fontWeight: 'bold',
          marginBottom: '16px',
          color: '#1a1a1a'
        }}>
          Online Exam Proctoring
        </h1>
        <p style={{
          fontSize: '20px',
          color: '#4a4a4a',
          marginBottom: '48px',
          lineHeight: '1.6'
        }}>
          Real-time media capture and WebSocket infrastructure for secure online examination
        </p>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: '24px',
          marginBottom: '48px'
        }}>
          <div style={{
            backgroundColor: 'white',
            borderRadius: '12px',
            padding: '32px',
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)'
          }}>
            <h2 style={{
              fontSize: '24px',
              fontWeight: '600',
              marginBottom: '12px',
              color: '#1a1a1a'
            }}>
              Candidate Portal
            </h2>
            <p style={{
              fontSize: '16px',
              color: '#4a4a4a',
              marginBottom: '24px',
              lineHeight: '1.6'
            }}>
              Join your exam session with real-time video and audio monitoring
            </p>
            <Link
              href="/candidate/demo-session-123?exam_id=exam-001"
              style={{
                display: 'inline-block',
                padding: '12px 24px',
                fontSize: '16px',
                fontWeight: '500',
                borderRadius: '8px',
                backgroundColor: '#0066cc',
                color: 'white',
                textDecoration: 'none',
                transition: 'background-color 0.2s'
              }}
            >
              Try Demo Session
            </Link>
          </div>

          <div style={{
            backgroundColor: 'white',
            borderRadius: '12px',
            padding: '32px',
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)'
          }}>
            <h2 style={{
              fontSize: '24px',
              fontWeight: '600',
              marginBottom: '12px',
              color: '#1a1a1a'
            }}>
              Invigilator Portal
            </h2>
            <p style={{
              fontSize: '16px',
              color: '#4a4a4a',
              marginBottom: '24px',
              lineHeight: '1.6'
            }}>
              Monitor candidates in real-time during exam sessions
            </p>
            <Link
              href="/invigilator/exam-001?invigilator_id=inv-123"
              style={{
                display: 'inline-block',
                padding: '12px 24px',
                fontSize: '16px',
                fontWeight: '500',
                borderRadius: '8px',
                backgroundColor: '#28a745',
                color: 'white',
                textDecoration: 'none',
                transition: 'background-color 0.2s'
              }}
            >
              Try Demo Monitor
            </Link>
          </div>
        </div>

        <div style={{
          backgroundColor: 'white',
          borderRadius: '12px',
          padding: '32px',
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
          textAlign: 'left'
        }}>
          <h2 style={{
            fontSize: '24px',
            fontWeight: '600',
            marginBottom: '16px',
            color: '#1a1a1a'
          }}>
            Features
          </h2>
          <ul style={{
            fontSize: '16px',
            color: '#4a4a4a',
            lineHeight: '1.8',
            paddingLeft: '24px'
          }}>
            <li>WebRTC media capture (webcam + microphone)</li>
            <li>Real-time WebSocket communication</li>
            <li>Permission request with consent banner</li>
            <li>Local video preview for candidates</li>
            <li>Audio level visualization</li>
            <li>Connection status monitoring</li>
            <li>Video frame streaming (configurable FPS)</li>
            <li>Graceful error handling and reconnection</li>
            <li>Browser compatibility checks</li>
          </ul>
        </div>
      </div>
    </div>
  )
}
