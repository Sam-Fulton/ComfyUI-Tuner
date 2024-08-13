import React, { useRef, useEffect } from 'react';
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

const SingleParameterChart = ({ paramName, paramData }) => {
    const chartRef = useRef(null);

    const labels = Object.keys(paramData);
    const goodData = labels.map(label => paramData[label].good);
    const badData = labels.map(label => paramData[label].bad);

    const data = {
        labels: labels,
        datasets: [
            {
                label: 'Good',
                data: goodData,
                backgroundColor: 'rgba(75, 192, 192, 0.6)',
                borderWidth: 1,
            },
            {
                label: 'Bad',
                data: badData,
                backgroundColor: 'rgba(255, 99, 132, 0.6)',
                borderWidth: 1,
            },
        ],
    };

    useEffect(() => {
        const chartInstance = chartRef.current;
        return () => {
            if (chartInstance) {
                chartInstance.destroy();
            }
        };
    }, []);

    return (
        <div style={{ marginBottom: '40px' }}>
            <h3>{paramName}</h3>
            <Bar ref={chartRef} data={data} options={{ indexAxis: 'y', stacked: true }} />
        </div>
    );
};

const ParameterChart = ({ getParameterCounts }) => {
    const paramCounts = getParameterCounts();
    
    // Debugging: log the paramCounts to verify structure
    console.log("Parameter Counts:", paramCounts);

    // If paramCounts is empty or undefined, render a message
    if (!paramCounts || Object.keys(paramCounts).length === 0) {
        return <p>No parameter data available.</p>;
    }

    return (
        <div>
            {Object.keys(paramCounts).map(paramName => (
                <SingleParameterChart
                    key={paramName}
                    paramName={paramName}
                    paramData={paramCounts[paramName]}
                />
            ))}
        </div>
    );
};

export default ParameterChart;
