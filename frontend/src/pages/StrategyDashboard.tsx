import React, { useState, useEffect } from 'react';
import { Table, Card, Button, Space, Tag, Statistic, Row, Col } from 'antd';
import { ReloadOutlined } from '@ant-design/icons';
import { getStrategies } from '../services/strategyService';
import { Strategy } from '../types/strategy';

const StrategyDashboard: React.FC = () => {
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    fetchStrategies();
  }, []);

  const fetchStrategies = async () => {
    try {
      setLoading(true);
      const response = await getStrategies();
      setStrategies(response.data);
    } catch (error) {
      console.error('Failed to fetch strategies:', error);
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

  const columns = [
    {
      title: '策略名称',
      dataIndex: 'name',
      key: 'name',
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
      render: (status: string) => getStatusTag(status),
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (text: string) => new Date(text).toLocaleString(),
    },
    {
      title: '更新时间',
      dataIndex: 'updated_at',
      key: 'updated_at',
      render: (text: string) => new Date(text).toLocaleString(),
    },
  ];

  return (
    <div>
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Card>
            <Statistic title="总策略数" value={strategies.length} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="活跃策略" 
              value={strategies.filter(s => s.status === 'active').length} 
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="暂停策略" 
              value={strategies.filter(s => s.status === 'paused').length} 
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="异常策略" 
              value={strategies.filter(s => s.status === 'error').length} 
            />
          </Card>
        </Col>
      </Row>

      <Card
        title="策略列表"
        extra={
          <Space>
            <Button 
              icon={<ReloadOutlined />} 
              onClick={fetchStrategies}
              loading={loading}
            >
              刷新
            </Button>
          </Space>
        }
      >
        <Table
          dataSource={strategies}
          columns={columns}
          rowKey="id"
          loading={loading}
        />
      </Card>
    </div>
  );
};

export default StrategyDashboard;