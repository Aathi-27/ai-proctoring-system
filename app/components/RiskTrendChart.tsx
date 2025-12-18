'use client';

import React from 'react';
import { LineChart, Line, XAxis, YAxis, ResponsiveContainer, CartesianGrid, Tooltip } from 'recharts';

interface RiskTrendChartProps {
  data: number[];
}

export function RiskTrendChart({ data }: RiskTrendChartProps) {
  const chartData = data.map((score, index) => ({
    time: index,
    score
  }));

  return (
    <ResponsiveContainer width="100%" height={150}>
      <LineChart
        data={chartData}
        margin={{ top: 5, right: 10, left: 0, bottom: 5 }}
      >
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        <XAxis
          dataKey="time"
          tick={{ fontSize: 10 }}
          hide={true}
        />
        <YAxis
          domain={[0, 100]}
          tick={{ fontSize: 10 }}
          width={30}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: '#fff',
            border: '1px solid #e5e7eb',
            borderRadius: '4px',
            fontSize: '12px'
          }}
          formatter={(value: number | undefined) => value !== undefined ? [`${Math.round(value)}`, 'Risk Score'] : ['N/A', 'Risk Score']}
        />
        <Line
          type="monotone"
          dataKey="score"
          stroke="#ef4444"
          dot={false}
          isAnimationActive={false}
          strokeWidth={2}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
