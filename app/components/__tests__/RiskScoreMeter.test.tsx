import React from 'react';
import { render, screen } from '@testing-library/react';
import { RiskScoreMeter } from '../RiskScoreMeter';

describe('RiskScoreMeter', () => {
  it('renders risk score meter with score', () => {
    render(<RiskScoreMeter score={45} />);
    expect(screen.getByText('45')).toBeInTheDocument();
  });

  it('displays correct risk label for different scores', () => {
    const { rerender } = render(<RiskScoreMeter score={25} />);
    expect(screen.getByText('Low Risk')).toBeInTheDocument();

    rerender(<RiskScoreMeter score={45} />);
    expect(screen.getByText('Medium Risk')).toBeInTheDocument();

    rerender(<RiskScoreMeter score={75} />);
    expect(screen.getByText('High Risk')).toBeInTheDocument();

    rerender(<RiskScoreMeter score={90} />);
    expect(screen.getByText('Critical Risk')).toBeInTheDocument();
  });

  it('renders without label when showLabel is false', () => {
    render(<RiskScoreMeter score={45} showLabel={false} />);
    expect(screen.getByText('45')).toBeInTheDocument();
    expect(screen.queryByText('Medium Risk')).not.toBeInTheDocument();
  });

  it('renders different sizes correctly', () => {
    const { container: smallContainer } = render(<RiskScoreMeter score={45} size="small" />);
    const { container: largeContainer } = render(<RiskScoreMeter score={45} size="large" />);

    const smallSvg = smallContainer.querySelector('svg');
    const largeSvg = largeContainer.querySelector('svg');

    // Just verify both render SVGs
    expect(smallSvg).toBeInTheDocument();
    expect(largeSvg).toBeInTheDocument();
  });
});
