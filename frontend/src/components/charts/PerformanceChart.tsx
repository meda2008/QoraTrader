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
  Filler,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface PerformanceChartProps {
  data: Array<{
    date: string;
    equity: number;
  }>;
}

const PerformanceChart: React.FC<PerformanceChartProps> = ({ data }) => {
  // 准备图表数据
  const chartData = {
    labels: data.map(item => new Date(item.date).toLocaleDateString()),
    datasets: [
      {
        label: '资金净值',
        data: data.map(item => item.equity),
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        fill: true,
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
        text: '资金净值曲线',
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

export default PerformanceChart;