'use client';

import React, { useRef } from 'react';
import type { ExamSession } from '@/app/types';
import { RiskScoreMeter } from './RiskScoreMeter';
import { RiskTrendChart } from './RiskTrendChart';

interface CandidateVideoFeedProps {
  session: ExamSession;
  currentRiskScore: number;
  elapsedTime: number;
}

export function CandidateVideoFeed({
  session,
  currentRiskScore,
  elapsedTime
}: CandidateVideoFeedProps) {
  const videoRef = useRef<HTMLDivElement>(null);

  const minutes = Math.floor(elapsedTime / 60);
  const seconds = elapsedTime % 60;
  const timeString = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;

  return (
    <div className="relative bg-gray-900 rounded-lg overflow-hidden border border-gray-700 w-full h-full flex flex-col">
      {/* Video Container */}
      <div
        ref={videoRef}
        className="flex-1 relative bg-black flex items-center justify-center"
      >
        <div className="absolute inset-0 flex items-center justify-center text-gray-500">
          <div className="text-center">
            <div className="text-2xl font-semibold mb-2">📹</div>
            <div className="text-sm">HD Video Stream</div>
            {session.videoStreamUrl && (
              <div className="text-xs text-gray-600 mt-2 max-w-[200px] break-all">
                {session.videoStreamUrl}
              </div>
            )}
          </div>
        </div>

        {/* Risk Score Overlay - Top Right */}
        <div className="absolute top-3 right-3 bg-black/60 rounded-lg p-3 backdrop-blur-sm">
          <div className="relative w-24 h-24">
            <RiskScoreMeter score={currentRiskScore} size="small" showLabel={false} />
          </div>
        </div>

        {/* Candidate Info - Bottom Left */}
        <div className="absolute bottom-3 left-3 bg-black/60 rounded-lg p-2 text-white text-xs backdrop-blur-sm">
          <div className="font-semibold">{session.candidateName}</div>
          <div className="text-gray-300">ID: {session.id}</div>
          <div className="text-gray-300">Time: {timeString}</div>
        </div>

        {/* Status Badge - Top Left */}
        {session.status !== 'active' && (
          <div className="absolute top-3 left-3">
            <div
              className={`px-2 py-1 rounded text-white text-xs font-semibold ${
                session.status === 'flagged'
                  ? 'bg-red-500/80'
                  : session.status === 'paused'
                    ? 'bg-yellow-500/80'
                    : ''
              }`}
            >
              {session.status.toUpperCase()}
            </div>
          </div>
        )}
      </div>

      {/* Risk Trend Chart */}
      <div className="bg-gray-800 border-t border-gray-700 p-2">
        <div className="text-xs text-gray-400 mb-1 px-1">Risk Trend (Last 5 min)</div>
        <RiskTrendChart data={session.riskTrend.slice(-30)} />
      </div>
    </div>
  );
}
