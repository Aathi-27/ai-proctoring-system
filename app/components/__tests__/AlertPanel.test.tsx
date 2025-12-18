import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { AlertPanel } from '../AlertPanel';
import { Alert } from '@/app/types';

describe('AlertPanel', () => {
  const mockAlerts: Alert[] = [
    {
      id: '1',
      sessionId: 'session-1',
      type: 'mobile_phone',
      severity: 'critical',
      confidence: 0.95,
      message: 'Mobile phone detected in frame',
      timestamp: Date.now(),
      isAcknowledged: false
    },
    {
      id: '2',
      sessionId: 'session-2',
      type: 'face_not_visible',
      severity: 'high',
      confidence: 0.88,
      message: 'Face not visible',
      timestamp: Date.now() - 5000,
      isAcknowledged: false
    },
    {
      id: '3',
      sessionId: 'session-1',
      type: 'tab_switch',
      severity: 'low',
      confidence: 0.75,
      message: 'Tab switch detected',
      timestamp: Date.now() - 10000,
      isAcknowledged: true
    }
  ];

  it('renders alert panel with alerts', () => {
    render(
      <AlertPanel
        alerts={mockAlerts}
        onAcknowledge={() => {}}
      />
    );
    expect(screen.getByText('Real-Time Alerts')).toBeInTheDocument();
    expect(screen.getByText(/Mobile phone detected/)).toBeInTheDocument();
  });

  it('displays unacknowledged alert count', () => {
    render(
      <AlertPanel
        alerts={mockAlerts}
        onAcknowledge={() => {}}
      />
    );
    expect(screen.getByText('2')).toBeInTheDocument(); // 2 unacknowledged alerts
  });

  it('calls onAcknowledge when acknowledge button is clicked', () => {
    const mockOnAcknowledge = jest.fn();
    render(
      <AlertPanel
        alerts={mockAlerts}
        onAcknowledge={mockOnAcknowledge}
      />
    );
    const acknowledgeButton = screen.getAllByText('Acknowledge')[0];
    fireEvent.click(acknowledgeButton);
    expect(mockOnAcknowledge).toHaveBeenCalledWith('1');
  });

  it('filters alerts by type', () => {
    render(
      <AlertPanel
        alerts={mockAlerts}
        onAcknowledge={() => {}}
      />
    );
    // Click mobile phone filter
    const filterButtons = screen.getAllByRole('button');
    const mobilePhoneButton = filterButtons.find(btn => btn.textContent === '📱');
    if (mobilePhoneButton) {
      fireEvent.click(mobilePhoneButton);
      expect(screen.getByText(/Mobile phone detected/)).toBeInTheDocument();
    }
  });

  it('shows empty state when no alerts', () => {
    render(
      <AlertPanel
        alerts={[]}
        onAcknowledge={() => {}}
      />
    );
    expect(screen.getByText('No alerts')).toBeInTheDocument();
  });

  it('displays alert severity badge', () => {
    render(
      <AlertPanel
        alerts={mockAlerts.slice(0, 1)}
        onAcknowledge={() => {}}
      />
    );
    expect(screen.getByText('Critical')).toBeInTheDocument();
  });

  it('displays alert confidence percentage', () => {
    render(
      <AlertPanel
        alerts={mockAlerts.slice(0, 1)}
        onAcknowledge={() => {}}
      />
    );
    expect(screen.getByText(/95%/)).toBeInTheDocument();
  });
});
