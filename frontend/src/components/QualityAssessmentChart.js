import React, { useMemo, useRef, useEffect } from 'react';
import { Bar } from 'react-chartjs-2';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend,
} from 'chart.js';

ChartJS.register(
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend
);

const QualityAssessmentChart = ({ qualityAssessments, getGoodBadCounts }) => {
    const chartRef = useRef(null);

    const data = useMemo(() => {
        if (qualityAssessments.length === 0) {
            return null;
        }

        const goodBadCounts = getGoodBadCounts();
        const labels = Object.keys(goodBadCounts);
        return {
            labels: labels,
            datasets: [
                {
                    label: 'Good',
                    data: labels.map((label) => goodBadCounts[label].good),
                    backgroundColor: 'rgba(75, 192, 192, 0.6)',
                    borderWidth: 1,
                },
                {
                    label: 'Bad',
                    data: labels.map((label) => goodBadCounts[label].bad),
                    backgroundColor: 'rgba(255, 99, 132, 0.6)',
                    borderWidth: 1,
                },
            ],
        };
    }, [qualityAssessments]);

    useEffect(() => {
        const chartInstance = chartRef.current;
        return () => {
            if (chartInstance) {
                chartInstance.destroy();
            }
        };
    }, []);

    if (!data) {
        return <p>No quality assessments available.</p>;
    }

    return <Bar ref={chartRef} data={data} />;
};

export default QualityAssessmentChart;
