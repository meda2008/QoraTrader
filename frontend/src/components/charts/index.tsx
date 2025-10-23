import React from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface ChartProps {
  data: Array<{
    date: string;
    value: number;
  }>;
  title: string;
  label: string;
  color: string;
}

const Chart: React.FC<ChartProps> = ({ data, title, label, color }) => {
  const chartData = {
    labels: data.map(item => new Date(item.date).toLocaleDateString()),
    datasets: [
      {
        label: label,
        data: data.map(item => item.value),
        borderColor: color,
        backgroundColor: color + '20', // 20% opacity for background
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: title,
      },
    },
    scales: {
      y: {
        beginAtZero: false,
      },
    },
  };

  return <Line data={chartData} options={options} />;
};

export default Chart;

export { default as PerformanceChart } from './PerformanceChart';
export { default as SignalVisualization } from '../SignalVisualization';