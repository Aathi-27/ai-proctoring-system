'use client';

import React, { useState } from 'react';
import type { Evidence } from '@/app/types';

interface EvidenceGalleryProps {
  evidences: Evidence[];
  maxHeight?: string;
}

export function EvidenceGallery({
  evidences,
  maxHeight = 'max-h-96'
}: EvidenceGalleryProps) {
  const [selectedEvidence, setSelectedEvidence] = useState<Evidence | null>(null);

  const sortedEvidences = [...evidences].sort((a, b) => b.timestamp - a.timestamp).slice(0, 20);

  return (
    <div className="flex flex-col h-full bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-50 to-pink-50 px-4 py-3 border-b border-gray-200">
        <div className="flex items-center gap-2">
          <span className="text-lg">📸</span>
          <h3 className="font-semibold text-gray-900">Evidence Gallery</h3>
          <span className="text-xs bg-purple-200 text-purple-900 rounded-full px-2 py-0.5">
            {sortedEvidences.length}
          </span>
        </div>
      </div>

      {/* Modal for full-size view */}
      {selectedEvidence && (
        <div
          className="fixed inset-0 bg-black/75 flex items-center justify-center z-50 p-4"
          onClick={() => setSelectedEvidence(null)}
        >
          <div
            className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-auto shadow-xl"
            onClick={e => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="sticky top-0 bg-gray-100 px-6 py-4 border-b border-gray-200 flex items-center justify-between">
              <h4 className="font-semibold text-gray-900">Evidence Details</h4>
              <button
                onClick={() => setSelectedEvidence(null)}
                className="text-gray-500 hover:text-gray-700 text-2xl"
              >
                ✕
              </button>
            </div>

            {/* Modal Content */}
            <div className="p-6">
              {/* Full-size image */}
              <div className="mb-6">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={selectedEvidence.imageUrl}
                  alt="Full evidence"
                  className="w-full h-auto rounded-lg border border-gray-200"
                  onError={(e) => {
                    (e.target as HTMLImageElement).src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="300"%3E%3Crect fill="%23e5e7eb" width="400" height="300"/%3E%3Ctext x="50%25" y="50%25" text-anchor="middle" dy=".3em" fill="%23999" font-family="Arial" font-size="16"%3EImage Failed to Load%3C/text%3E%3C/svg%3E';
                  }}
                />
              </div>

              {/* Metadata */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <span className="text-xs text-gray-600 block">Timestamp</span>
                  <div className="text-sm font-semibold text-gray-900 mt-1">
                    {new Date(selectedEvidence.timestamp).toLocaleString()}
                  </div>
                </div>
                <div>
                  <span className="text-xs text-gray-600 block">Event Type</span>
                  <div className="text-sm font-semibold text-gray-900 mt-1">
                    {selectedEvidence.eventType.replace(/_/g, ' ')}
                  </div>
                </div>
                <div>
                  <span className="text-xs text-gray-600 block">Risk Score</span>
                  <div className="text-sm font-semibold text-gray-900 mt-1">
                    {Math.round(selectedEvidence.riskScoreAtCapture)}
                  </div>
                </div>
                <div>
                  <span className="text-xs text-gray-600 block">Session ID</span>
                  <div className="text-sm font-semibold text-gray-900 mt-1 truncate">
                    {selectedEvidence.sessionId}
                  </div>
                </div>
              </div>

              {/* Download button */}
              <div className="mt-6 flex gap-2">
                <a
                  href={selectedEvidence.imageUrl}
                  download
                  className="flex-1 px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded text-sm font-semibold transition-colors"
                >
                  Download Evidence
                </a>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Gallery Grid */}
      <div className={`flex-1 overflow-y-auto ${maxHeight}`}>
        {sortedEvidences.length === 0 ? (
          <div className="flex items-center justify-center h-full text-gray-500 text-sm">
            No evidence snapshots available
          </div>
        ) : (
          <div className="p-4 grid grid-cols-4 gap-3">
            {sortedEvidences.map((evidence) => (
              <div
                key={evidence.id}
                className="relative group cursor-pointer aspect-video bg-gray-100 rounded-lg overflow-hidden border border-gray-200 hover:border-purple-400 transition-colors"
                onClick={() => setSelectedEvidence(evidence)}
              >
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={evidence.thumbnailUrl || evidence.imageUrl}
                  alt="Evidence thumbnail"
                  className="w-full h-full object-cover group-hover:scale-110 transition-transform"
                  onError={(e) => {
                    (e.target as HTMLImageElement).src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="160" height="90"%3E%3Crect fill="%23e5e7eb" width="160" height="90"/%3E%3Ctext x="50%25" y="50%25" text-anchor="middle" dy=".3em" fill="%23999" font-family="Arial" font-size="10"%3ENo Image%3C/text%3E%3C/svg%3E';
                  }}
                />

                {/* Overlay on hover */}
                <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                  <div className="text-white text-2xl">👁️</div>
                </div>

                {/* Timestamp label */}
                <div className="absolute bottom-1 left-1 right-1 bg-black/60 text-white text-xs px-1 py-0.5 rounded truncate">
                  {new Date(evidence.timestamp).toLocaleTimeString()}
                </div>

                {/* Risk score indicator */}
                <div className="absolute top-1 right-1 bg-black/60 text-white text-xs font-semibold px-1.5 py-0.5 rounded">
                  {Math.round(evidence.riskScoreAtCapture)}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="bg-gray-50 border-t border-gray-200 px-4 py-2 text-xs text-gray-600">
        Showing {sortedEvidences.length} recent snapshots
      </div>
    </div>
  );
}
