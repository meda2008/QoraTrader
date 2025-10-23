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

interface SignalVisualizationProps {
  priceData: Array<{
    date: string;
    open: number;
    high: number;
    low: number;
    close: number;
  }>;
  signals: Array<{
    date: string;
    type: 'buy' | 'sell';
    price: number;
  }>;
  trades: Array<{
    date: string;
    type: 'buy' | 'sell';
    price: number;
    quantity: number;
  }>;
}

const SignalVisualization: React.FC<SignalVisualizationProps> = ({ 
  priceData, 
  signals, 
  trades 
}) => {
  // 准备价格数据
  const priceChartData = {
    labels: priceData.map(item => new Date(item.date).toLocaleDateString()),
    datasets: [
      {
        label: '价格',
        data: priceData.map(item => item.close),
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        fill: false,
      },
    ],
  };

  // 添加信号点到图表
  const signalBuyPoints = signals
    .filter(signal => signal.type === 'buy')
    .map(signal => ({
      x: new Date(signal.date).toLocaleDateString(),
      y: signal.price,
    }));

  const signalSellPoints = signals
    .filter(signal => signal.type === 'sell')
    .map(signal => ({
      x: new Date(signal.date).toLocaleDateString(),
      y: signal.price,
    }));

  // 添加成交点到图表
  const tradeBuyPoints = trades
    .filter(trade => trade.type === 'buy')
    .map(trade => ({
      x: new Date(trade.date).toLocaleDateString(),
      y: trade.price,
    }));

  const tradeSellPoints = trades
    .filter(trade => trade.type === 'sell')
    .map(trade => ({
      x: new Date(trade.date).toLocaleDateString(),
      y: trade.price,
    }));

  // 合并所有数据到图表
  const chartData = {
    labels: priceData.map(item => new Date(item.date).toLocaleDateString()),
    datasets: [
      {
        label: '价格',
        data: priceData.map(item => item.close),
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        fill: false,
        borderWidth: 2,
      },
      {
        label: '买入信号',
        data: signalBuyPoints,
        pointBackgroundColor: 'green',
        pointRadius: 6,
        pointStyle: 'triangle',
        showLine: false,
      },
      {
        label: '卖出信号',
        data: signalSellPoints,
        pointBackgroundColor: 'red',
        pointRadius: 6,
        pointStyle: 'triangle',
        showLine: false,
      },
      {
        label: '买入成交',
        data: tradeBuyPoints,
        pointBackgroundColor: 'lightgreen',
        pointRadius: 4,
        pointStyle: 'rect',
        showLine: false,
      },
      {
        label: '卖出成交',
        data: tradeSellPoints,
        pointBackgroundColor: 'pink',
        pointRadius: 4,
        pointStyle: 'rect',
        showLine: false,
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
        text: '策略信号与成交可视化',
      },
      tooltip: {
        mode: 'index' as const,
        intersect: false,
      },
    },
    scales: {
      y: {
        beginAtZero: false,
      },
    },
    interaction: {
      mode: 'nearest' as const,
      axis: 'x' as const,
      intersect: false,
    },
  };

  return <Line data={chartData} options={options} />;
};

export default SignalVisualization;