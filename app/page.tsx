'use client';

import { InvigilatorDashboard } from '@/app/components/InvigilatorDashboard';
import { WebSocketProvider } from '@/app/context/WebSocketContext';

export default function Home() {
  return (
    <WebSocketProvider>
      <InvigilatorDashboard />
    </WebSocketProvider>
  );
}
