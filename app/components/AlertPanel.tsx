'use client';

import React, { useState, useMemo } from 'react';
import type { Alert } from '@/app/types';

interface AlertPanelProps {
  alerts: Alert[];
  onAcknowledge: (alertId: string) => void;
  maxHeight?: string;
}

const alertTypeIcons: Record<string, string> = {
  mobile_phone: '📱',
  face_not_visible: '👤',
  multiple_faces: '👥',
  copied_text: '📋',
  tab_switch: '📑',
  inactivity: '⏸️',
  audio_anomaly: '🔊',
  manual: '✋'
};

const alertTypeLabels: Record<string, string> = {
  mobile_phone: 'Mobile Phone Detected',
  face_not_visible: 'Face Not Visible',
  multiple_faces: 'Multiple Faces',
  copied_text: 'Copy/Paste Activity',
  tab_switch: 'Tab Switched',
  inactivity: 'Inactivity',
  audio_anomaly: 'Audio Anomaly',
  manual: 'Manual Note'
};

function getSeverityColor(severity: Alert['severity']): string {
  switch (severity) {
    case 'critical':
      return 'bg-red-100 border-red-300 text-red-900';
    case 'high':
      return 'bg-orange-100 border-orange-300 text-orange-900';
    case 'medium':
      return 'bg-yellow-100 border-yellow-300 text-yellow-900';
    case 'low':
      return 'bg-blue-100 border-blue-300 text-blue-900';
  }
}

function getSeverityBadgeColor(severity: Alert['severity']): string {
  switch (severity) {
    case 'critical':
      return 'bg-red-500';
    case 'high':
      return 'bg-orange-500';
    case 'medium':
      return 'bg-yellow-500';
    case 'low':
      return 'bg-blue-500';
  }
}

export function AlertPanel({
  alerts,
  onAcknowledge,
  maxHeight = 'max-h-96'
}: AlertPanelProps) {
  const [filterType, setFilterType] = useState<string | null>(null);

  const filteredAlerts = useMemo(() => {
    if (!filterType) return alerts;
    return alerts.filter(alert => alert.type === filterType);
  }, [alerts, filterType]);

  const unacknowledgedCount = alerts.filter(a => !a.isAcknowledged).length;

  return (
    <div className="flex flex-col h-full bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-red-50 to-orange-50 px-4 py-3 border-b border-gray-200">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <span className="text-lg">⚠️</span>
            <h3 className="font-semibold text-gray-900">Real-Time Alerts</h3>
            {unacknowledgedCount > 0 && (
              <span className="inline-flex items-center justify-center w-5 h-5 text-xs font-bold text-white bg-red-500 rounded-full">
                {unacknowledgedCount}
              </span>
            )}
          </div>
        </div>

        {/* Filter buttons */}
        <div className="flex gap-1 flex-wrap">
          <button
            onClick={() => setFilterType(null)}
            className={`text-xs px-2 py-1 rounded transition-colors ${
              filterType === null
                ? 'bg-red-500 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            All
          </button>
          {Object.entries(alertTypeIcons).map(([type]) => (
            <button
              key={type}
              onClick={() => setFilterType(type)}
              className={`text-xs px-2 py-1 rounded transition-colors ${
                filterType === type
                  ? 'bg-red-500 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {alertTypeIcons[type as keyof typeof alertTypeIcons]}
            </button>
          ))}
        </div>
      </div>

      {/* Alert List */}
      <div className={`flex-1 overflow-y-auto ${maxHeight}`}>
        {filteredAlerts.length === 0 ? (
          <div className="flex items-center justify-center h-full text-gray-500 text-sm">
            {alerts.length === 0 ? 'No alerts' : 'No alerts matching filter'}
          </div>
        ) : (
          <div className="divide-y divide-gray-100">
            {filteredAlerts.map((alert) => (
              <div
                key={alert.id}
                className={`p-3 border-l-4 transition-all ${getSeverityColor(alert.severity)} ${
                  alert.isAcknowledged ? 'opacity-60' : ''
                }`}
                style={{ borderLeftColor: getSeverityBadgeColor(alert.severity) }}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start gap-2">
                      <span className="text-lg flex-shrink-0 mt-0.5">
                        {alertTypeIcons[alert.type as keyof typeof alertTypeIcons] || '❗'}
                      </span>
                      <div className="flex-1 min-w-0">
                        <div className="font-semibold text-sm">
                          {alertTypeLabels[alert.type as keyof typeof alertTypeLabels] || alert.type}
                        </div>
                        <div className="text-xs mt-1 opacity-80 break-words">
                          {alert.message}
                          {alert.confidence && (
                            <div className="mt-1">
                              Confidence: {Math.round(alert.confidence * 100)}%
                            </div>
                          )}
                        </div>
                        <div className="text-xs opacity-60 mt-1">
                          {new Date(alert.timestamp).toLocaleTimeString()}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Severity Badge and Actions */}
                  <div className="flex flex-col items-end gap-2 flex-shrink-0">
                    <span className={`px-2 py-1 rounded text-white text-xs font-semibold ${getSeverityBadgeColor(alert.severity)}`}>
                      {alert.severity.charAt(0).toUpperCase() + alert.severity.slice(1)}
                    </span>

                    {!alert.isAcknowledged && (
                      <button
                        onClick={() => onAcknowledge(alert.id)}
                        className="px-2 py-1 bg-blue-500 hover:bg-blue-600 text-white text-xs rounded transition-colors"
                      >
                        Acknowledge
                      </button>
                    )}

                    {alert.snapshot && (
                      <a
                        href={alert.snapshot}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="px-2 py-1 bg-gray-500 hover:bg-gray-600 text-white text-xs rounded transition-colors"
                      >
                        Evidence
                      </a>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="bg-gray-50 border-t border-gray-200 px-4 py-2 text-xs text-gray-600">
        Showing {filteredAlerts.length} of {alerts.length} alerts
      </div>
    </div>
  );
}
