import React, { useState, useEffect } from 'react';
import { Card, Table, Tabs, Statistic, Row, Col, Button, Space, Tag, DatePicker } from 'antd';
import { ReloadOutlined, DownloadOutlined } from '@ant-design/icons';
import { useParams } from 'react-router-dom';
import { getStrategyDetails, getStrategyPerformance } from '../services/strategyService';
import { Strategy } from '../types/strategy';
import { PerformanceData } from '../types/performance';
import { PerformanceChart } from '../components/charts/PerformanceChart';

const { TabPane } = Tabs;
const { RangePicker } = DatePicker;

const StrategyDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [strategy, setStrategy] = useState<Strategy | null>(null);
  const [performance, setPerformance] = useState<PerformanceData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [dateRange, setDateRange] = useState<[moment.Moment, moment.Moment] | null>(null);

  useEffect(() => {
    fetchStrategyDetails();
  }, [id, dateRange]);

  const fetchStrategyDetails = async () => {
    try {
      setLoading(true);
      const strategyResponse = await getStrategyDetails(id!);
      setStrategy(strategyResponse.data);

      const performanceResponse = await getStrategyPerformance(id!, dateRange);
      setPerformance(performanceResponse.data);
    } catch (error) {
      console.error('Failed to fetch strategy details:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusTag = (status: string) => {
    switch (status) {
      case 'active':
        return <Tag color="green">活跃</Tag>;
      case 'inactive':
        return <Tag color="default">未激活</Tag>;
      case 'paused':
        return <Tag color="orange">暂停</Tag>;
      case 'stopped':
        return <Tag color="red">已停止</Tag>;
      case 'error':
        return <Tag color="red">异常</Tag>;
      default:
        return <Tag color="default">{status}</Tag>;
    }
  };

  const renderBasicInfo = () => (
    <Card title="基本信息" style={{ marginBottom: 16 }}>
      <Row gutter={16}>
        <Col span={8}>
          <Statistic title="策略名称" value={strategy?.name} />
        </Col>
        <Col span={8}>
          <Statistic title="状态" value={strategy?.status} valueStyle={{ color: strategy?.status === 'active' ? 'green' : 'blue' }} />
        </Col>
        <Col span={8}>
          <Statistic title="创建时间" value={strategy?.created_at} />
        </Col>
      </Row>
      <Row gutter={16} style={{ marginTop: 16 }}>
        <Col span={24}>
          <div><strong>描述:</strong> {strategy?.description}</div>
        </Col>
      </Row>
    </Card>
  );

  const renderPerformanceMetrics = () => (
    <Card title="性能指标" style={{ marginBottom: 16 }}>
      {performance && (
        <Row gutter={16}>
          <Col span={6}>
            <Statistic title="总收益" value={performance.total_return} precision={2} suffix="%" />
          </Col>
          <Col span={6}>
            <Statistic title="夏普比率" value={performance.sharpe_ratio} precision={2} />
          </Col>
          <Col span={6}>
            <Statistic title="最大回撤" value={performance.max_drawdown} precision={2} suffix="%" />
          </Col>
          <Col span={6}>
            <Statistic title="胜率" value={performance.win_rate} precision={2} suffix="%" />
          </Col>
        </Row>
      )}
    </Card>
  );

  const renderPerformanceChart = () => (
    <Card title="资金净值曲线" style={{ marginBottom: 16 }}>
      {performance && <PerformanceChart data={performance.equity_curve} />}
    </Card>
  );

  const renderTradeHistory = () => {
    const tradeColumns = [
      {
        title: '时间',
        dataIndex: 'timestamp',
        key: 'timestamp',
        render: (text: string) => new Date(text).toLocaleString(),
      },
      {
        title: '交易标的',
        dataIndex: 'symbol',
        key: 'symbol',
      },
      {
        title: '方向',
        dataIndex: 'side',
        key: 'side',
        render: (side: string) => (
          <Tag color={side === 'buy' ? 'green' : 'red'}>
            {side === 'buy' ? '买入' : '卖出'}
          </Tag>
        ),
      },
      {
        title: '数量',
        dataIndex: 'quantity',
        key: 'quantity',
      },
      {
        title: '价格',
        dataIndex: 'price',
        key: 'price',
      },
      {
        title: '盈亏',
        dataIndex: 'pnl',
        key: 'pnl',
        render: (pnl: number) => (
          <span style={{ color: pnl >= 0 ? 'green' : 'red' }}>
            {pnl >= 0 ? '+' : ''}{pnl.toFixed(2)}
          </span>
        ),
      },
    ];

    return (
      <Card title="交易历史">
        <Table
          columns={tradeColumns}
          dataSource={performance?.trades || []}
          rowKey="id"
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
          onClick={fetchStrategyDetails}
          loading={loading}
        >
          刷新
        </Button>
        <Button icon={<DownloadOutlined />}>
          导出报告
        </Button>
        <RangePicker
          onChange={(dates) => {
            if (dates && dates[0] && dates[1]) {
              setDateRange([dates[0], dates[1]]);
            } else {
              setDateRange(null);
            }
          }}
        />
      </Space>

      {strategy && renderBasicInfo()}
      {performance && renderPerformanceMetrics()}
      {performance && renderPerformanceChart()}

      <Tabs defaultActiveKey="1">
        <TabPane tab="交易历史" key="1">
          {renderTradeHistory()}
        </TabPane>
        <TabPane tab="回测报告" key="2">
          <Card title="回测详情">
            回测报告内容
          </Card>
        </TabPane>
        <TabPane tab="参数配置" key="3">
          <Card title="参数">
            策略参数配置
          </Card>
        </TabPane>
      </Tabs>
    </div>
  );
};

export default StrategyDetails;