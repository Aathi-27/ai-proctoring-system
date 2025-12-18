'use client';

import React, { useMemo } from 'react';

interface RiskScoreMeterProps {
  score: number;
  size?: 'small' | 'medium' | 'large';
  showLabel?: boolean;
}

function getRiskColor(score: number): string {
  if (score < 30) return '#10b981'; // Green
  if (score < 60) return '#f59e0b'; // Yellow
  if (score < 85) return '#f97316'; // Orange
  return '#ef4444'; // Red
}

function getRiskLabel(score: number): string {
  if (score < 30) return 'Low Risk';
  if (score < 60) return 'Medium Risk';
  if (score < 85) return 'High Risk';
  return 'Critical Risk';
}

export function RiskScoreMeter({ score, size = 'medium', showLabel = true }: RiskScoreMeterProps) {
  const sizeConfig = useMemo(() => {
    switch (size) {
      case 'small':
        return { radius: 20, strokeWidth: 3, fontSize: '10px', labelSize: '12px' };
      case 'large':
        return { radius: 50, strokeWidth: 4, fontSize: '28px', labelSize: '14px' };
      case 'medium':
      default:
        return { radius: 35, strokeWidth: 4, fontSize: '18px', labelSize: '13px' };
    }
  }, [size]);

  const color = getRiskColor(score);
  const label = getRiskLabel(score);
  const circumference = 2 * Math.PI * sizeConfig.radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  const containerSize = (sizeConfig.radius + sizeConfig.strokeWidth) * 2;

  return (
    <div className="flex flex-col items-center justify-center">
      <svg
        width={containerSize}
        height={containerSize}
        className="transform -rotate-90"
      >
        {/* Background circle */}
        <circle
          cx={containerSize / 2}
          cy={containerSize / 2}
          r={sizeConfig.radius}
          fill="none"
          stroke="#e5e7eb"
          strokeWidth={sizeConfig.strokeWidth}
        />
        {/* Progress circle */}
        <circle
          cx={containerSize / 2}
          cy={containerSize / 2}
          r={sizeConfig.radius}
          fill="none"
          stroke={color}
          strokeWidth={sizeConfig.strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          className="transition-all duration-300"
        />
      </svg>
      
      {/* Score text in center */}
      <div className="absolute flex flex-col items-center justify-center">
        <div style={{ fontSize: sizeConfig.fontSize }} className="font-bold text-gray-900">
          {Math.round(score)}
        </div>
        {showLabel && (
          <div style={{ fontSize: sizeConfig.labelSize }} className="text-gray-600 mt-1">
            {label}
          </div>
        )}
      </div>
    </div>
  );
}
