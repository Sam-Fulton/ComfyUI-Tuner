import React from 'react';
import { render, screen } from '@testing-library/react';
import QualityAssessmentChart from '../../components/QualityAssessmentChart';

if (!HTMLCanvasElement.prototype.getContext) {
  HTMLCanvasElement.prototype.getContext = () => {
    return {
      clearRect: () => {},
      fillRect: () => {},
      getImageData: () => {},
      putImageData: () => {},
      createImageData: () => {},
      setTransform: () => {},
      drawImage: () => {},
      save: () => {},
      fillText: () => {},
      restore: () => {},
      beginPath: () => {},
      moveTo: () => {},
      lineTo: () => {},
      closePath: () => {},
      stroke: () => {},
    };
  };
}

describe('QualityAssessmentChart', () => {
  test('renders no data message when qualityAssessments is empty', () => {
    const dummyGetGoodBadCounts = jest.fn();
    render(
      <QualityAssessmentChart 
        qualityAssessments={[]} 
        getGoodBadCounts={dummyGetGoodBadCounts} 
      />
    );
    expect(screen.getByText(/No quality assessments available/i)).toBeInTheDocument();
    expect(dummyGetGoodBadCounts).not.toHaveBeenCalled();
  });

  test('renders chart when qualityAssessments is non-empty', () => {
    const sampleQualityAssessments = [{ id: 1 }];
    const goodBadCounts = {
      Label1: { good: 5, bad: 3 },
      Label2: { good: 2, bad: 6 }
    };
    const dummyGetGoodBadCounts = jest.fn().mockReturnValue(goodBadCounts);
    const { container } = render(
      <QualityAssessmentChart 
        qualityAssessments={sampleQualityAssessments} 
        getGoodBadCounts={dummyGetGoodBadCounts} 
      />
    );

    expect(dummyGetGoodBadCounts).toHaveBeenCalled();
    const canvas = container.querySelector('canvas');
    expect(canvas).toBeInTheDocument();
  });
});
