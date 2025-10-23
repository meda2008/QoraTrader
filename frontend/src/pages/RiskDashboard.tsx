import React, { useState, useEffect } from 'react';
import { Card, Table, Statistic, Row, Col, Tag, Progress, Button, Space } from 'antd';
import { ReloadOutlined, AlertOutlined } from '@ant-design/icons';
import { getRiskMetrics, getRiskAlerts } from '../services/riskService';
import { RiskMetric, RiskAlert } from '../types/risk';

const RiskDashboard: React.FC = () => {
  const [riskMetrics, setRiskMetrics] = useState<RiskMetric[]>([]);
  const [riskAlerts, setRiskAlerts] = useState<RiskAlert[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    fetchRiskData();
  }, []);

  const fetchRiskData = async () => {
    try {
      setLoading(true);
      const metricsResponse = await getRiskMetrics();
      setRiskMetrics(metricsResponse.data);

      const alertsResponse = await getRiskAlerts();
      setRiskAlerts(alertsResponse.data);
    } catch (error) {
      console.error('Failed to fetch risk data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRiskLevelColor = (level: string) => {
    switch (level) {
      case 'low':
        return '#52c41a';
      case 'medium':
        return '#faad14';
      case 'high':
        return '#ff4d4f';
      case 'extreme':
        return '#f5222d';
      default:
        return '#d9d9d9';
    }
  };

  const getRiskLevelTag = (level: string) => {
    switch (level) {
      case 'low':
        return <Tag color="green">低风险</Tag>;
      case 'medium':
        return <Tag color="orange">中风险</Tag>;
      case 'high':
        return <Tag color="red">高风险</Tag>;
      case 'extreme':
        return <Tag color="red">极高风险</Tag>;
      default:
        return <Tag>{level}</Tag>;
    }
  };

  const renderRiskMetrics = () => {
    const totalAccounts = riskMetrics.length;
    const highRiskAccounts = riskMetrics.filter(m => m.risk_level === 'high' || m.risk_level === 'extreme').length;
    const exposure = riskMetrics.reduce((sum, metric) => sum + (metric.exposure || 0), 0);
    const dailyLoss = riskMetrics.reduce((sum, metric) => sum + (metric.daily_pnl || 0), 0);

    return (
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic title="监控账户数" value={totalAccounts} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="高风险账户" 
              value={highRiskAccounts} 
              valueStyle={{ color: '#cf1322' }} 
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="总风险敞口" 
              value={exposure} 
              precision={2}
              valueStyle={{ color: exposure > 100000 ? '#cf1322' : '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="当日盈亏" 
              value={dailyLoss} 
              precision={2}
              valueStyle={{ color: dailyLoss >= 0 ? '#3f8600' : '#cf1322' }}
            />
          </Card>
        </Col>
      </Row>
    );
  };

  const renderRiskExposureChart = () => {
    const totalExposure = riskMetrics.reduce((sum, metric) => sum + (metric.exposure || 0), 0);
    const maxExposureLimit = 1000000; // 假设最大敞口限制为100万

    return (
      <Card title="风险敞口监控" style={{ marginBottom: 16 }}>
        <div style={{ marginBottom: 16 }}>
          <div>当前总敞口: ¥{totalExposure.toLocaleString()}</div>
          <div>最大敞口限制: ¥{maxExposureLimit.toLocaleString()}</div>
        </div>
        <Progress 
          percent={Math.min(100, (totalExposure / maxExposureLimit) * 100)} 
          status={totalExposure > maxExposureLimit * 0.8 ? 'exception' : 'active'} 
        />
      </Card>
    );
  };

  const renderAlerts = () => {
    const alertColumns = [
      {
        title: '时间',
        dataIndex: 'timestamp',
        key: 'timestamp',
        render: (text: string) => new Date(text).toLocaleString(),
      },
      {
        title: '类型',
        dataIndex: 'type',
        key: 'type',
      },
      {
        title: '严重程度',
        dataIndex: 'severity',
        key: 'severity',
        render: (severity: string) => getRiskLevelTag(severity),
      },
      {
        title: '描述',
        dataIndex: 'description',
        key: 'description',
      },
      {
        title: '状态',
        dataIndex: 'status',
        key: 'status',
        render: (status: string) => (
          <Tag color={status === 'resolved' ? 'green' : 'red'}>
            {status === 'resolved' ? '已解决' : '待处理'}
          </Tag>
        ),
      },
    ];

    return (
      <Card title="风险告警">
        <Table
          dataSource={riskAlerts}
          columns={alertColumns}
          rowKey="id"
          pagination={{ pageSize: 10 }}
        />
      </Card>
    );
  };

  const renderMetricsTable = () => {
    const columns = [
      {
        title: '账户',
        dataIndex: 'account_id',
        key: 'account_id',
      },
      {
        title: '账户类型',
        dataIndex: 'account_type',
        key: 'account_type',
      },
      {
        title: '风险等级',
        dataIndex: 'risk_level',
        key: 'risk_level',
        render: (level: string) => getRiskLevelTag(level),
      },
      {
        title: '风险敞口',
        dataIndex: 'exposure',
        key: 'exposure',
        render: (value: number) => `¥${value?.toLocaleString() || '0'}`,
      },
      {
        title: 'VaR',
        dataIndex: 'var',
        key: 'var',
        render: (value: number) => `${value?.toFixed(2) || '0.00'}%`,
      },
      {
        title: '当日盈亏',
        dataIndex: 'daily_pnl',
        key: 'daily_pnl',
        render: (value: number) => (
          <span style={{ color: value >= 0 ? 'green' : 'red' }}>
            ¥{value?.toLocaleString() || '0.00'}
          </span>
        ),
      },
    ];

    return (
      <Card title="风险指标详情">
        <Table
          dataSource={riskMetrics}
          columns={columns}
          rowKey="account_id"
          pagination={{ pageSize: 10 }}
        />
      </Card>
    );
  };

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <Button 
          icon={<ReloadOutlined />} 
          onClick={fetchRiskData}
          loading={loading}
        >
          刷新
        </Button>
      </Space>

      {renderRiskMetrics()}
      {renderRiskExposureChart()}

      {riskMetrics.length > 0 && renderMetricsTable()}
      {riskAlerts.length > 0 && renderAlerts()}
    </div>
  );
};

export default RiskDashboard;