import React from 'react';
import { Card, Statistic, Row, Col, Progress, Table, Tag } from 'antd';
import { ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons';

interface RiskVisualizationProps {
  riskData: Array<{
    account_id: string;
    risk_level: string;
    exposure: number;
    var_value: number;
    daily_pnl: number;
  }>;
}

const RiskVisualization: React.FC<RiskVisualizationProps> = ({ riskData }) => {
  // 计算总体风险指标
  const totalExposure = riskData.reduce((sum, item) => sum + (item.exposure || 0), 0);
  const totalDailyPnL = riskData.reduce((sum, item) => sum + (item.daily_pnl || 0), 0);
  const highRiskCount = riskData.filter(item => item.risk_level === 'high' || item.risk_level === 'extreme').length;

  const getRiskLevelColor = (level: string) => {
    switch (level) {
      case 'low':
        return 'green';
      case 'medium':
        return 'orange';
      case 'high':
        return 'red';
      case 'extreme':
        return 'red-inverse';
      default:
        return 'default';
    }
  };

  const riskColumns = [
    {
      title: '账户ID',
      dataIndex: 'account_id',
      key: 'account_id',
    },
    {
      title: '风险等级',
      dataIndex: 'risk_level',
      key: 'risk_level',
      render: (level: string) => (
        <Tag color={getRiskLevelColor(level)}>
          {level === 'low' ? '低' : level === 'medium' ? '中' : level === 'high' ? '高' : level === 'extreme' ? '极高' : level}
        </Tag>
      ),
    },
    {
      title: '风险敞口',
      dataIndex: 'exposure',
      key: 'exposure',
      render: (value: number) => `¥${value?.toLocaleString() || '0'}`,
    },
    {
      title: 'VaR',
      dataIndex: 'var_value',
      key: 'var_value',
      render: (value: number) => `${value?.toFixed(2) || '0.00'}%`,
    },
    {
      title: '当日盈亏',
      dataIndex: 'daily_pnl',
      key: 'daily_pnl',
      render: (value: number) => (
        <span style={{ color: value >= 0 ? 'green' : 'red' }}>
          {value >= 0 ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
          ¥{Math.abs(value || 0).toLocaleString()}
        </span>
      ),
    },
  ];

  return (
    <div>
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={8}>
          <Card>
            <Statistic 
              title="总风险敞口" 
              value={totalExposure} 
              precision={2}
              valueStyle={{ color: totalExposure > 1000000 ? '#cf1322' : '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic 
              title="高风险账户数" 
              value={highRiskCount} 
              valueStyle={{ color: highRiskCount > 0 ? '#cf1322' : '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic 
              title="当日盈亏" 
              value={totalDailyPnL} 
              precision={2}
              valueStyle={totalDailyPnL >= 0 ? { color: '#3f8600' } : { color: '#cf1322' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={24}>
          <Card title="风险敞口分布">
            <Progress 
              percent={Math.min(100, (totalExposure / 5000000) * 100)} 
              status={totalExposure > 4000000 ? 'exception' : totalExposure > 3000000 ? 'active' : 'success'} 
              format={percent => `总敞口: ¥${totalExposure.toLocaleString()} (${percent}%)`}
            />
          </Card>
        </Col>
      </Row>

      <Card title="账户风险详情">
        <Table 
          dataSource={riskData} 
          columns={riskColumns} 
          rowKey="account_id"
          pagination={{ pageSize: 10 }}
        />
      </Card>
    </div>
  );
};

export default RiskVisualization;