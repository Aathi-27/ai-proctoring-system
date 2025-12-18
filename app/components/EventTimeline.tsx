'use client';

import React, { useState, useMemo } from 'react';
import type { TimelineEvent } from '@/app/types';

interface EventTimelineProps {
  events: TimelineEvent[];
  maxHeight?: string;
}

const eventTypeIcons: Record<string, string> = {
  mobile_phone: '📱',
  face_not_visible: '👤',
  multiple_faces: '👥',
  copied_text: '📋',
  tab_switch: '📑',
  inactivity: '⏸️',
  audio_anomaly: '🔊',
  manual: '✋',
  alert: '⚠️'
};

function getSeverityColor(severity: TimelineEvent['severity']): {
  dot: string;
  bg: string;
  text: string;
} {
  switch (severity) {
    case 'critical':
      return { dot: 'bg-red-500', bg: 'bg-red-50', text: 'text-red-900' };
    case 'high':
      return { dot: 'bg-orange-500', bg: 'bg-orange-50', text: 'text-orange-900' };
    case 'medium':
      return { dot: 'bg-yellow-500', bg: 'bg-yellow-50', text: 'text-yellow-900' };
    case 'low':
      return { dot: 'bg-blue-500', bg: 'bg-blue-50', text: 'text-blue-900' };
  }
}

export function EventTimeline({ events, maxHeight = 'max-h-96' }: EventTimelineProps) {
  const [expandedEventId, setExpandedEventId] = useState<string | null>(null);
  const [timeFilter, setTimeFilter] = useState<'all' | 'critical' | 'high'>('all');

  const filteredEvents = useMemo(() => {
    if (timeFilter === 'all') return events;
    if (timeFilter === 'critical') {
      return events.filter(e => e.severity === 'critical');
    }
    if (timeFilter === 'high') {
      return events.filter(e => ['critical', 'high'].includes(e.severity));
    }
    return events;
  }, [events, timeFilter]);

  const sortedEvents = useMemo(() => {
    return [...filteredEvents].sort((a, b) => b.timestamp - a.timestamp);
  }, [filteredEvents]);

  return (
    <div className="flex flex-col h-full bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 px-4 py-3 border-b border-gray-200">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <span className="text-lg">📊</span>
            <h3 className="font-semibold text-gray-900">Event Timeline</h3>
            <span className="text-xs bg-blue-200 text-blue-900 rounded-full px-2 py-0.5">
              {sortedEvents.length}
            </span>
          </div>
        </div>

        {/* Filter buttons */}
        <div className="flex gap-2">
          {(['all', 'critical', 'high'] as const).map((filter) => (
            <button
              key={filter}
              onClick={() => setTimeFilter(filter)}
              className={`text-xs px-3 py-1 rounded transition-colors ${
                timeFilter === filter
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {filter.charAt(0).toUpperCase() + filter.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Timeline */}
      <div className={`flex-1 overflow-y-auto ${maxHeight}`}>
        {sortedEvents.length === 0 ? (
          <div className="flex items-center justify-center h-full text-gray-500 text-sm">
            No events to display
          </div>
        ) : (
          <div className="p-4 space-y-3">
            {sortedEvents.map((event, index) => {
              const severityColors = getSeverityColor(event.severity);
              const isExpanded = expandedEventId === event.id;

              return (
                <div key={event.id} className="relative">
                  {/* Timeline connector line (except for last item) */}
                  {index < sortedEvents.length - 1 && (
                    <div
                      className={`absolute left-4 top-8 w-0.5 h-8 ${severityColors.dot}`}
                      style={{ opacity: 0.3 }}
                    />
                  )}

                  {/* Timeline item */}
                  <div
                    className={`relative pl-10 pb-3 border-l-2 border-transparent cursor-pointer transition-colors hover:${severityColors.bg} rounded p-2 -ml-2 ${
                      isExpanded ? severityColors.bg : ''
                    }`}
                    onClick={() => setExpandedEventId(isExpanded ? null : event.id)}
                  >
                    {/* Timeline dot */}
                    <div
                      className={`absolute left-0 top-1 w-3 h-3 rounded-full ${severityColors.dot} border-2 border-white`}
                    />

                    {/* Event header */}
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-2">
                        <span className="text-base">
                          {eventTypeIcons[event.eventType as keyof typeof eventTypeIcons] || '📌'}
                        </span>
                        <div>
                          <div className="font-semibold text-sm text-gray-900">
                            {event.eventType
                              .replace(/_/g, ' ')
                              .split(' ')
                              .map(w => w.charAt(0).toUpperCase() + w.slice(1))
                              .join(' ')}
                          </div>
                          <div className="text-xs text-gray-600">
                            {new Date(event.timestamp).toLocaleTimeString()}
                          </div>
                        </div>
                      </div>
                      <span
                        className={`px-2 py-1 rounded text-xs font-semibold text-white ${severityColors.dot}`}
                      >
                        {event.severity.charAt(0).toUpperCase() + event.severity.slice(1)}
                      </span>
                    </div>

                    {/* Expandable details */}
                    {isExpanded && (
                      <div className="mt-3 pt-3 border-t border-gray-200 space-y-2">
                        <div className="grid grid-cols-2 gap-2 text-xs">
                          <div>
                            <span className="text-gray-600">Confidence:</span>
                            <div className="font-semibold text-gray-900">
                              {Math.round(event.confidence * 100)}%
                            </div>
                          </div>
                          <div>
                            <span className="text-gray-600">Risk Contribution:</span>
                            <div className="font-semibold text-gray-900">
                              +{Math.round(event.riskContribution)}
                            </div>
                          </div>
                          <div>
                            <span className="text-gray-600">Session:</span>
                            <div className="font-semibold text-gray-900 truncate">
                              {event.sessionId}
                            </div>
                          </div>
                          <div>
                            <span className="text-gray-600">Time:</span>
                            <div className="font-semibold text-gray-900">
                              {new Date(event.timestamp).toLocaleString()}
                            </div>
                          </div>
                        </div>

                        {event.snapshot && (
                          <div className="mt-3 pt-3 border-t border-gray-200">
                            <a
                              href={event.snapshot}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-block px-3 py-1 bg-blue-500 hover:bg-blue-600 text-white text-xs rounded transition-colors"
                            >
                              View Evidence
                            </a>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="bg-gray-50 border-t border-gray-200 px-4 py-2 text-xs text-gray-600">
        Showing {sortedEvents.length} of {events.length} events
      </div>
    </div>
  );
}
