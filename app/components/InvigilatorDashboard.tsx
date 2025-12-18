/* eslint-disable react-hooks/set-state-in-effect */
'use client';

import React, { useEffect, useState, useCallback, useMemo } from 'react';
import { useWebSocket } from '@/app/context/WebSocketContext';
import type { ExamSession, ExamInfo, Evidence } from '@/app/types';
import { CandidateVideoFeed } from './CandidateVideoFeed';
import { AlertPanel } from './AlertPanel';
import { EventTimeline } from './EventTimeline';
import { EvidenceGallery } from './EvidenceGallery';
import { SessionSidebar } from './SessionSidebar';

export function InvigilatorDashboard() {
  const { isConnected, alerts, events, sessionUpdates, scoreUpdates, acknowledgeAlert, sendMessage } = useWebSocket();

  const [examInfo, setExamInfo] = useState<ExamInfo>({
    id: 'exam-001',
    name: 'Mathematics Final Exam',
    startTime: 0,
    duration: 3600000,
    totalCandidates: 0,
    activeCandidates: 0
  });

  const [sessions, setSessions] = useState<ExamSession[]>([]);
  const [selectedSessionId, setSelectedSessionId] = useState<string | null>(null);
  const [evidences, setEvidences] = useState<Evidence[]>([]);
  const [elapsedTimes, setElapsedTimes] = useState<Record<string, number>>({});

  // Initialize with mock data
  useEffect(() => {
    const now = Date.now();
    const mockSessions: ExamSession[] = [
      {
        id: 'session-001',
        candidateId: 'candidate-001',
        candidateName: 'John Smith',
        sessionStartTime: now - 300000,
        currentRiskScore: 45,
        status: 'active',
        videoStreamUrl: 'https://example.com/stream/john-smith.m3u8',
        riskTrend: [10, 12, 15, 18, 25, 30, 28, 32, 40, 45]
      },
      {
        id: 'session-002',
        candidateId: 'candidate-002',
        candidateName: 'Emily Johnson',
        sessionStartTime: now - 320000,
        currentRiskScore: 78,
        status: 'active',
        videoStreamUrl: 'https://example.com/stream/emily-johnson.m3u8',
        riskTrend: [15, 18, 25, 35, 45, 55, 65, 72, 75, 78]
      },
      {
        id: 'session-003',
        candidateId: 'candidate-003',
        candidateName: 'Michael Brown',
        sessionStartTime: now - 280000,
        currentRiskScore: 25,
        status: 'active',
        videoStreamUrl: 'https://example.com/stream/michael-brown.m3u8',
        riskTrend: [5, 8, 10, 12, 15, 20, 22, 25, 24, 25]
      },
      {
        id: 'session-004',
        candidateId: 'candidate-004',
        candidateName: 'Sarah Davis',
        sessionStartTime: now - 400000,
        currentRiskScore: 92,
        status: 'flagged',
        videoStreamUrl: 'https://example.com/stream/sarah-davis.m3u8',
        riskTrend: [20, 35, 50, 65, 75, 80, 85, 88, 90, 92]
      }
    ];

    setSessions(mockSessions);
    setExamInfo(prev => ({
      ...prev,
      startTime: now - 300000,
      totalCandidates: mockSessions.length,
      activeCandidates: mockSessions.length
    }));
    setSelectedSessionId(mockSessions[0].id);

    // Mock evidence data
    const mockEvidences: Evidence[] = [
      {
        id: 'ev-001',
        sessionId: 'session-002',
        timestamp: now - 60000,
        eventType: 'mobile_phone',
        riskScoreAtCapture: 75,
        imageUrl: 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="320" height="240"%3E%3Crect fill="%23ff6b6b" width="320" height="240"/%3E%3Ctext x="50%25" y="50%25" text-anchor="middle" dy=".3em" fill="%23fff" font-family="Arial" font-size="16"%3EMobile Detected%3C/text%3E%3C/svg%3E'
      },
      {
        id: 'ev-002',
        sessionId: 'session-004',
        timestamp: now - 120000,
        eventType: 'multiple_faces',
        riskScoreAtCapture: 88,
        imageUrl: 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="320" height="240"%3E%3Crect fill="%23ffa500" width="320" height="240"/%3E%3Ctext x="50%25" y="50%25" text-anchor="middle" dy=".3em" fill="%23fff" font-family="Arial" font-size="16"%3EMultiple Faces%3C/text%3E%3C/svg%3E'
      }
    ];
    setEvidences(mockEvidences);
  }, []);

  // Update elapsed times
  useEffect(() => {
    const interval = setInterval(() => {
      setElapsedTimes(prev => {
        const updated = { ...prev };
        sessions.forEach(session => {
          const elapsed = Math.floor((Date.now() - session.sessionStartTime) / 1000);
          updated[session.id] = elapsed;
        });
        return updated;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [sessions]);

  // Update sessions from WebSocket
  useEffect(() => {
    if (sessionUpdates.length > 0) {
      setSessions(prev => {
        const updated = [...prev];
        sessionUpdates.forEach(wsSession => {
          const index = updated.findIndex(s => s.id === wsSession.id);
          if (index >= 0) {
            updated[index] = wsSession;
          } else {
            updated.push(wsSession);
          }
        });
        return updated;
      });
    }
  }, [sessionUpdates]);

  // Apply score updates
  useEffect(() => {
    const entries = Object.entries(scoreUpdates);
    if (entries.length > 0) {
      setSessions(prev =>
        prev.map(session => {
          if (scoreUpdates[session.id] !== undefined) {
            return {
              ...session,
              currentRiskScore: scoreUpdates[session.id],
              riskTrend: [...session.riskTrend, scoreUpdates[session.id]].slice(-30)
            };
          }
          return session;
        })
      );
    }
  }, [scoreUpdates]);

  const selectedSession = useMemo(() => {
    return sessions.find(s => s.id === selectedSessionId);
  }, [sessions, selectedSessionId]);

  const handlePauseSession = useCallback((sessionId: string) => {
    setSessions(prev =>
      prev.map(s =>
        s.id === sessionId ? { ...s, status: s.status === 'paused' ? 'active' : 'paused' } : s
      )
    );
    sendMessage({
      type: 'session_update',
      data: { action: 'pause', sessionId }
    });
  }, [sendMessage]);

  const handleFlagSession = useCallback((sessionId: string) => {
    setSessions(prev =>
      prev.map(s =>
        s.id === sessionId ? { ...s, status: s.status === 'flagged' ? 'active' : 'flagged' } : s
      )
    );
    sendMessage({
      type: 'session_update',
      data: { action: 'flag', sessionId }
    });
  }, [sendMessage]);

  const handleLogout = useCallback(() => {
    console.log('Logout initiated');
    // Handle logout logic
  }, []);

  const elapsedTime = selectedSession ? (elapsedTimes[selectedSession.id] || 0) : 0;
  const currentScore = selectedSession ? scoreUpdates[selectedSession.id] ?? selectedSession.currentRiskScore : 0;

  return (
    <div className="flex flex-col h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{examInfo.name}</h1>
              <div className="text-sm text-gray-600 mt-1">
                Started {new Date(examInfo.startTime).toLocaleTimeString()} · {examInfo.activeCandidates} / {examInfo.totalCandidates} candidates active
              </div>
            </div>

            {/* Status indicator */}
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
                <span className="text-sm text-gray-600">
                  {isConnected ? 'Connected' : 'Disconnected'}
                </span>
              </div>

              {/* Keyboard shortcuts info */}
              <div className="text-xs text-gray-500 px-3 py-1 bg-gray-50 rounded">
                Alt+P: Pause | Alt+F: Flag
              </div>

              {/* Logout button */}
              <button
                onClick={handleLogout}
                className="px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded text-sm font-semibold transition-colors"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <div className="flex flex-1 gap-4 p-4 overflow-hidden">
        {/* Left Sidebar - Sessions */}
        <div className="w-64 flex-shrink-0">
          <SessionSidebar
            sessions={sessions}
            selectedSessionId={selectedSessionId}
            onSelectSession={setSelectedSessionId}
            onPauseSession={handlePauseSession}
            onFlagSession={handleFlagSession}
            maxHeight="max-h-[calc(100vh-200px)]"
          />
        </div>

        {/* Center - Video feeds and info */}
        <div className="flex-1 flex flex-col gap-4 overflow-hidden">
          {/* Video grid */}
          <div className="flex-1 grid grid-cols-2 gap-4 overflow-hidden">
            {/* Main selected video - larger */}
            <div className="col-span-2 lg:col-span-1">
              {selectedSession ? (
                <CandidateVideoFeed
                  session={selectedSession}
                  currentRiskScore={currentScore}
                  elapsedTime={elapsedTime}
                />
              ) : (
                <div className="bg-gray-800 rounded-lg border border-gray-700 flex items-center justify-center text-gray-400">
                  No session selected
                </div>
              )}
            </div>

            {/* Additional video feeds grid */}
            <div className="col-span-2 lg:col-span-1 grid grid-cols-2 gap-2 overflow-hidden">
              {sessions
                .filter(s => s.id !== selectedSessionId)
                .slice(0, 4)
                .map(session => (
                  <div
                    key={session.id}
                    onClick={() => setSelectedSessionId(session.id)}
                    className="cursor-pointer hover:ring-2 hover:ring-blue-500 transition-all rounded-lg overflow-hidden"
                  >
                    <div className="relative bg-gray-800 h-full min-h-[120px] flex items-center justify-center">
                      <div className="text-gray-400 text-xs text-center px-2">
                        <div>{session.candidateName}</div>
                        <div className="text-yellow-400 mt-1">Risk: {Math.round(session.currentRiskScore)}</div>
                      </div>
                    </div>
                  </div>
                ))}
            </div>
          </div>

          {/* Timeline scrubber (placeholder) */}
          <div className="bg-white rounded-lg border border-gray-200 p-3 flex items-center gap-2">
            <span className="text-xs font-semibold text-gray-600">Timeline:</span>
            <div className="flex-1 h-1 bg-gray-200 rounded-full relative cursor-pointer group">
              <div className="absolute left-0 top-1/2 transform -translate-y-1/2 w-3 h-3 bg-blue-500 rounded-full shadow group-hover:w-4 group-hover:h-4" />
            </div>
            <span className="text-xs text-gray-600">
              {new Date(examInfo.startTime + elapsedTime * 1000).toLocaleTimeString()}
            </span>
          </div>
        </div>

        {/* Right Panel */}
        <div className="w-80 flex-shrink-0 flex flex-col gap-4 overflow-hidden">
          {/* Alerts */}
          <div className="flex-1 min-h-0">
            <AlertPanel
              alerts={alerts}
              onAcknowledge={acknowledgeAlert}
              maxHeight="max-h-[calc(50vh-100px)]"
            />
          </div>

          {/* Timeline Events */}
          <div className="flex-1 min-h-0">
            <EventTimeline
              events={events}
              maxHeight="max-h-[calc(50vh-100px)]"
            />
          </div>
        </div>
      </div>

      {/* Bottom panel - Evidence gallery */}
      <div className="border-t border-gray-200 bg-gray-100 h-48 p-4">
        <EvidenceGallery
          evidences={evidences}
          maxHeight="max-h-40"
        />
      </div>
    </div>
  );
}
