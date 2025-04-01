import React from 'react';
import { render, screen } from '@testing-library/react';
import ParameterChart from '../../components/ParameterChart.js'

describe('ParameterChart', () => {
  test('renders no data message when getParameterCounts returns empty object', () => {
    const getParameterCounts = () => ({});
    render(<ParameterChart getParameterCounts={getParameterCounts} />);
    expect(screen.getByText(/No parameter data available/i)).toBeInTheDocument();
  });

  test('renders parameter charts when getParameterCounts returns data', () => {
    const sampleCounts = {
      parameter1: {
        label1: { good: 3, bad: 1 },
        label2: { good: 5, bad: 2 },
      },
      parameter2: {
        labelA: { good: 2, bad: 4 },
      },
    };

    const getParameterCounts = () => sampleCounts;
    render(<ParameterChart getParameterCounts={getParameterCounts} />);

    expect(screen.getByText('parameter1')).toBeInTheDocument();
    expect(screen.getByText('parameter2')).toBeInTheDocument();
  });
});
