import React from 'react';
import { Card, Statistic, Row, Col, Table, Tag } from 'antd';
import { ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons';

interface StrategyDashboardProps {
  strategies: Array<{
    id: string;
    name: string;
    status: string;
    dailyPnL: number;
    totalReturn: number;
    lastUpdated: string;
  }>;
}

const StrategyDashboard: React.FC<StrategyDashboardProps> = ({ strategies }) => {
  // 从策略数据中计算统计信息
  const activeStrategies = strategies.filter(s => s.status === 'active');
  const totalDailyPnL = strategies.reduce((sum, strategy) => sum + strategy.dailyPnL, 0);
  const totalReturn = strategies.reduce((sum, strategy) => sum + strategy.totalReturn, 0);

  const columns = [
    {
      title: '策略名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        let color = 'default';
        if (status === 'active') color = 'green';
        if (status === 'inactive') color = 'default';
        if (status === 'paused') color = 'orange';
        if (status === 'stopped') color = 'red';
        if (status === 'error') color = 'red';
        return <Tag color={color}>{status}</Tag>;
      },
    },
    {
      title: '日盈亏',
      dataIndex: 'dailyPnL',
      key: 'dailyPnL',
      render: (value: number) => (
        <span style={{ color: value >= 0 ? 'green' : 'red' }}>
          {value >= 0 ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
          {Math.abs(value).toFixed(2)}
        </span>
      ),
    },
    {
      title: '总收益',
      dataIndex: 'totalReturn',
      key: 'totalReturn',
      render: (value: number) => (
        <span style={{ color: value >= 0 ? 'green' : 'red' }}>
          {value >= 0 ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
          {Math.abs(value).toFixed(2)}
        </span>
      ),
    },
    {
      title: '最后更新',
      dataIndex: 'lastUpdated',
      key: 'lastUpdated',
      render: (text: string) => new Date(text).toLocaleString(),
    },
  ];

  return (
    <div>
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic title="总策略数" value={strategies.length} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="活跃策略" value={activeStrategies.length} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="日盈亏总额" 
              value={totalDailyPnL} 
              precision={2}
              valueStyle={{ color: totalDailyPnL >= 0 ? '#3f8600' : '#cf1322' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="总收益" 
              value={totalReturn} 
              precision={2}
              valueStyle={{ color: totalReturn >= 0 ? '#3f8600' : '#cf1322' }}
            />
          </Card>
        </Col>
      </Row>

      <Card title="策略详情">
        <Table 
          dataSource={strategies} 
          columns={columns} 
          rowKey="id"
          pagination={{ pageSize: 10 }}
        />
      </Card>
    </div>
  );
};

export default StrategyDashboard;