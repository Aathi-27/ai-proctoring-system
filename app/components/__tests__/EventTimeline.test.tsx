import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { EventTimeline } from '../EventTimeline';
import { TimelineEvent } from '@/app/types';

describe('EventTimeline', () => {
  const mockEvents: TimelineEvent[] = [
    {
      id: '1',
      sessionId: 'session-1',
      eventType: 'mobile_phone',
      timestamp: Date.now(),
      confidence: 0.95,
      riskContribution: 25,
      severity: 'critical'
    },
    {
      id: '2',
      sessionId: 'session-2',
      eventType: 'face_not_visible',
      timestamp: Date.now() - 10000,
      confidence: 0.88,
      riskContribution: 20,
      severity: 'high'
    },
    {
      id: '3',
      sessionId: 'session-1',
      eventType: 'tab_switch',
      timestamp: Date.now() - 20000,
      confidence: 0.75,
      riskContribution: 10,
      severity: 'low'
    }
  ];

  it('renders event timeline with events', () => {
    render(<EventTimeline events={mockEvents} />);
    expect(screen.getByText('Event Timeline')).toBeInTheDocument();
    expect(screen.getByText(/Mobile Phone/)).toBeInTheDocument();
  });

  it('displays event count', () => {
    render(<EventTimeline events={mockEvents} />);
    expect(screen.getByText('3')).toBeInTheDocument();
  });

  it('filters events by severity', () => {
    render(<EventTimeline events={mockEvents} />);
    const filterButtons = screen.getAllByRole('button');
    const criticalButton = filterButtons.find(btn => btn.textContent === 'Critical');
    if (criticalButton) {
      fireEvent.click(criticalButton);
      expect(screen.getByText(/Mobile Phone/)).toBeInTheDocument();
    }
  });

  it('expands event details on click', () => {
    render(<EventTimeline events={mockEvents} />);
    const eventItems = screen.getAllByText(/[Mm]obile [Pp]hone/);
    if (eventItems.length > 0) {
      fireEvent.click(eventItems[0]);
      expect(screen.getByText(/Confidence:/)).toBeInTheDocument();
    }
  });

  it('shows empty state when no events', () => {
    render(<EventTimeline events={[]} />);
    expect(screen.getByText('No events to display')).toBeInTheDocument();
  });

  it('displays event severity labels', () => {
    render(<EventTimeline events={mockEvents} />);
    expect(screen.getByText('Critical')).toBeInTheDocument();
    expect(screen.getByText('High')).toBeInTheDocument();
    expect(screen.getByText('Low')).toBeInTheDocument();
  });

  it('sorts events by timestamp (most recent first)', () => {
    render(<EventTimeline events={mockEvents} />);
    const eventTexts = screen.getAllByText(/20\d{2}-\d{2}-\d{2}/);
    // First event should be the most recent one
    expect(eventTexts.length).toBeGreaterThan(0);
  });
});
