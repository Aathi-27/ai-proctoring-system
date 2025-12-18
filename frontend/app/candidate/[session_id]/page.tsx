'use client';

import { useParams, useSearchParams } from 'next/navigation';
import MediaCapture from '@/components/MediaCapture';

export default function CandidatePage() {
  const params = useParams();
  const searchParams = useSearchParams();
  
  const sessionId = params.session_id as string;
  const examId = searchParams.get('exam_id') || undefined;

  const handlePermissionGranted = () => {
    console.log('Permission granted');
  };

  const handlePermissionDenied = () => {
    console.log('Permission denied');
    alert('Camera and microphone access is required to proceed with the exam.');
  };

  const handleError = (error: Error) => {
    console.error('Media capture error:', error);
  };

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f8f9fa' }}>
      <header style={{
        backgroundColor: 'white',
        borderBottom: '1px solid #e0e0e0',
        padding: '16px 24px',
        boxShadow: '0 2px 4px rgba(0, 0, 0, 0.05)'
      }}>
        <div style={{
          maxWidth: '1200px',
          margin: '0 auto',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <h1 style={{
            fontSize: '20px',
            fontWeight: 'bold',
            color: '#1a1a1a'
          }}>
            Online Exam Proctoring - Candidate
          </h1>
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
      </header>

      <main style={{ padding: '24px' }}>
        <MediaCapture
          sessionId={sessionId}
          examId={examId}
          wsBaseURL={process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'}
          videoQuality="medium"
          fps={10}
          onPermissionGranted={handlePermissionGranted}
          onPermissionDenied={handlePermissionDenied}
          onError={handleError}
        />
      </main>
    </div>
  );
}
