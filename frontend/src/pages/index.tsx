import Link from 'next/link';

export default function Home() {
  return (
    <div style={{ 
      minHeight: '100vh', 
      display: 'flex', 
      flexDirection: 'column',
      alignItems: 'center', 
      justifyContent: 'center',
      backgroundColor: '#f5f5f5',
      fontFamily: 'system-ui, -apple-system, sans-serif'
    }}>
      <div style={{ 
        textAlign: 'center',
        padding: '40px',
        backgroundColor: 'white',
        borderRadius: '12px',
        boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
        maxWidth: '600px'
      }}>
        <h1 style={{ fontSize: '48px', marginBottom: '20px', color: '#333' }}>
          Exam Activity Monitoring
        </h1>
        <p style={{ fontSize: '18px', color: '#666', marginBottom: '30px', lineHeight: '1.6' }}>
          A comprehensive browser-level monitoring system for online exams that tracks 
          tab switching, copy-paste events, and user inactivity.
        </p>
        
        <div style={{ marginBottom: '30px' }}>
          <h2 style={{ fontSize: '24px', marginBottom: '15px', color: '#333' }}>Features</h2>
          <ul style={{ 
            textAlign: 'left', 
            display: 'inline-block',
            lineHeight: '2',
            color: '#555'
          }}>
            <li>📊 Tab/Window visibility detection</li>
            <li>📋 Copy-paste event logging</li>
            <li>⏱️ Keyboard & mouse inactivity tracking</li>
            <li>🔐 Privacy-first implementation</li>
            <li>🌐 Real-time WebSocket communication</li>
          </ul>
        </div>

        <Link 
          href="/exam"
          style={{
            display: 'inline-block',
            backgroundColor: '#2196F3',
            color: 'white',
            padding: '15px 40px',
            borderRadius: '8px',
            textDecoration: 'none',
            fontSize: '18px',
            fontWeight: 'bold',
            transition: 'background-color 0.3s'
          }}
        >
          Start Demo Exam
        </Link>

        <div style={{ 
          marginTop: '30px', 
          padding: '20px',
          backgroundColor: '#fff3cd',
          borderRadius: '8px',
          border: '1px solid #ffc107'
        }}>
          <p style={{ margin: 0, fontSize: '14px', color: '#856404' }}>
            <strong>Note:</strong> This is a demonstration. The monitoring features will 
            track your activity on the exam page.
          </p>
        </div>
      </div>
    </div>
  );
}
