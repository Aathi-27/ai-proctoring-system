'use client';

import React, { useState } from 'react';
import type { ExamSession } from '@/app/types';
import { RiskScoreMeter } from './RiskScoreMeter';

interface SessionSidebarProps {
  sessions: ExamSession[];
  selectedSessionId?: string | null;
  onSelectSession: (sessionId: string) => void;
  onPauseSession: (sessionId: string) => void;
  onFlagSession: (sessionId: string) => void;
  maxHeight?: string;
}

export function SessionSidebar({
  sessions,
  selectedSessionId,
  onSelectSession,
  onPauseSession,
  onFlagSession,
  maxHeight = 'max-h-96'
}: SessionSidebarProps) {
  const [expandedSessionId, setExpandedSessionId] = useState<string | null>(null);

  const sortedSessions = [...sessions].sort((a, b) => b.currentRiskScore - a.currentRiskScore);

  return (
    <div className="flex flex-col h-full bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-green-50 to-teal-50 px-4 py-3 border-b border-gray-200">
        <div className="flex items-center gap-2">
          <span className="text-lg">👥</span>
          <h3 className="font-semibold text-gray-900">Active Sessions</h3>
          <span className="text-xs bg-green-200 text-green-900 rounded-full px-2 py-0.5">
            {sortedSessions.length}
          </span>
        </div>
      </div>

      {/* Sessions List */}
      <div className={`flex-1 overflow-y-auto ${maxHeight}`}>
        {sortedSessions.length === 0 ? (
          <div className="flex items-center justify-center h-full text-gray-500 text-sm">
            No active sessions
          </div>
        ) : (
          <div className="divide-y divide-gray-100">
            {sortedSessions.map((session) => {
              const isSelected = selectedSessionId === session.id;
              const isExpanded = expandedSessionId === session.id;

              return (
                <div
                  key={session.id}
                  className={`p-3 transition-colors border-l-4 ${
                    isSelected
                      ? 'bg-blue-50 border-l-blue-500'
                      : 'hover:bg-gray-50 border-l-transparent'
                  } ${
                    session.status === 'flagged'
                      ? 'bg-red-50/50'
                      : session.status === 'paused'
                        ? 'bg-yellow-50/50'
                        : ''
                  }`}
                >
                  {/* Main row */}
                  <div
                    className="cursor-pointer"
                    onClick={() => {
                      onSelectSession(session.id);
                      setExpandedSessionId(isExpanded ? null : session.id);
                    }}
                  >
                    <div className="flex items-center justify-between gap-2">
                      {/* Session info and risk score */}
                      <div className="flex-1 min-w-0">
                        <div className="font-semibold text-sm text-gray-900 truncate">
                          {session.candidateName}
                        </div>
                        <div className="text-xs text-gray-600 truncate">
                          ID: {session.id}
                        </div>
                      </div>

                      {/* Risk score meter */}
                      <div className="flex-shrink-0 w-16 h-16">
                        <RiskScoreMeter score={session.currentRiskScore} size="small" showLabel={false} />
                      </div>
                    </div>

                    {/* Status badges */}
                    {session.status !== 'active' && (
                      <div className="mt-2 flex gap-1">
                        {session.status === 'flagged' && (
                          <span className="inline-block px-2 py-1 bg-red-500 text-white text-xs rounded font-semibold">
                            🚩 FLAGGED
                          </span>
                        )}
                        {session.status === 'paused' && (
                          <span className="inline-block px-2 py-1 bg-yellow-500 text-white text-xs rounded font-semibold">
                            ⏸️ PAUSED
                          </span>
                        )}
                      </div>
                    )}
                  </div>

                  {/* Expandable action buttons */}
                  {isExpanded && (
                    <div className="mt-3 pt-3 border-t border-gray-200 space-y-2">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onPauseSession(session.id);
                        }}
                        disabled={session.status === 'paused'}
                        className={`w-full px-3 py-2 text-xs rounded font-semibold transition-colors ${
                          session.status === 'paused'
                            ? 'bg-gray-200 text-gray-600 cursor-not-allowed'
                            : 'bg-yellow-500 hover:bg-yellow-600 text-white'
                        }`}
                      >
                        ⏸️ Pause Exam
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onFlagSession(session.id);
                        }}
                        disabled={session.status === 'flagged'}
                        className={`w-full px-3 py-2 text-xs rounded font-semibold transition-colors ${
                          session.status === 'flagged'
                            ? 'bg-gray-200 text-gray-600 cursor-not-allowed'
                            : 'bg-red-500 hover:bg-red-600 text-white'
                        }`}
                      >
                        🚩 Flag Session
                      </button>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="bg-gray-50 border-t border-gray-200 px-4 py-2 text-xs text-gray-600">
        {sortedSessions.length} active session{sortedSessions.length !== 1 ? 's' : ''}
      </div>
    </div>
  );
}
