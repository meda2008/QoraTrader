import React, { useState, useEffect } from 'react';
import { Card, Table, Tabs, Button, Space, DatePicker, Select, message } from 'antd';
import { ReloadOutlined, DownloadOutlined, FilterOutlined } from '@ant-design/icons';
import { getReports, getReportById } from '../services/reportService';
import { Report } from '../types/report';

const { TabPane } = Tabs;
const { RangePicker } = DatePicker;
const { Option } = Select;

const ReportsPage: React.FC = () => {
  const [reports, setReports] = useState<Report[]>([]);
  const [selectedReport, setSelectedReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [dateRange, setDateRange] = useState<[moment.Moment, moment.Moment] | null>(null);
  const [reportType, setReportType] = useState<string>('');

  useEffect(() => {
    fetchReports();
  }, [dateRange, reportType]);

  const fetchReports = async () => {
    try {
      setLoading(true);
      const response = await getReports({
        startDate: dateRange ? dateRange[0].toISOString() : undefined,
        endDate: dateRange ? dateRange[1].toISOString() : undefined,
        type: reportType,
      });
      setReports(response.data);
    } catch (error) {
      console.error('Failed to fetch reports:', error);
      message.error('获取报表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleReportSelect = async (reportId: string) => {
    try {
      const response = await getReportById(reportId);
      setSelectedReport(response.data);
    } catch (error) {
      console.error('Failed to fetch report:', error);
      message.error('获取报表详情失败');
    }
  };

  const reportColumns = [
    {
      title: '报表名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
    },
    {
      title: '生成时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (text: string) => new Date(text).toLocaleString(),
    },
    {
      title: '策略',
      dataIndex: 'strategy_name',
      key: 'strategy_name',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
    },
    {
      title: '操作',
      key: 'actions',
      render: (text: any, record: Report) => (
        <Button 
          type="link" 
          onClick={() => handleReportSelect(record.id)}
        >
          查看详情
        </Button>
      ),
    },
  ];

  const getReportDetailContent = () => {
    if (!selectedReport) {
      return <div>请选择一个报表查看详细信息</div>;
    }

    return (
      <div>
        <Card title={selectedReport.name} style={{ marginBottom: 16 }}>
          <p><strong>类型:</strong> {selectedReport.type}</p>
          <p><strong>策略:</strong> {selectedReport.strategy_name}</p>
          <p><strong>生成时间:</strong> {new Date(selectedReport.created_at).toLocaleString()}</p>
          <p><strong>状态:</strong> {selectedReport.status}</p>
          {selectedReport.description && <p><strong>描述:</strong> {selectedReport.description}</p>}
        </Card>

        {/* 根据报表类型显示不同内容 */}
        {selectedReport.type === 'performance' && (
          <Card title="绩效指标">
            <p>年化收益率: {selectedReport.metrics?.annual_return}%</p>
            <p>夏普比率: {selectedReport.metrics?.sharpe_ratio}</p>
            <p>最大回撤: {selectedReport.metrics?.max_drawdown}%</p>
            <p>胜率: {selectedReport.metrics?.win_rate}%</p>
          </Card>
        )}

        {selectedReport.type === 'trade' && (
          <Card title="交易详情">
            <Table
              dataSource={selectedReport.trades || []}
              columns={[
                { title: '时间', dataIndex: 'timestamp', key: 'timestamp' },
                { title: '交易标的', dataIndex: 'symbol', key: 'symbol' },
                { title: '方向', dataIndex: 'side', key: 'side' },
                { title: '数量', dataIndex: 'quantity', key: 'quantity' },
                { title: '价格', dataIndex: 'price', key: 'price' },
                { title: '盈亏', dataIndex: 'pnl', key: 'pnl' },
              ]}
              rowKey="id"
            />
          </Card>
        )}
      </div>
    );
  };

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <Button 
          icon={<ReloadOutlined />} 
          onClick={fetchReports}
          loading={loading}
        >
          刷新
        </Button>
        <Button icon={<DownloadOutlined />}>
          批量导出
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
        <Select
          placeholder="报表类型"
          style={{ width: 200 }}
          onChange={setReportType}
          allowClear
        >
          <Option value="performance">绩效报表</Option>
          <Option value="trade">交易报表</Option>
          <Option value="risk">风险报表</Option>
          <Option value="pnl">盈亏报表</Option>
        </Select>
        <Button icon={<FilterOutlined />}>
          高级筛选
        </Button>
      </Space>

      <Tabs defaultActiveKey="1">
        <TabPane tab="报表列表" key="1">
          <Card>
            <Table
              dataSource={reports}
              columns={reportColumns}
              rowKey="id"
              loading={loading}
              pagination={{ pageSize: 10 }}
            />
          </Card>
        </TabPane>
        <TabPane tab="报表详情" key="2">
          <Card>
            {getReportDetailContent()}
          </Card>
        </TabPane>
      </Tabs>
    </div>
  );
};

export default ReportsPage;