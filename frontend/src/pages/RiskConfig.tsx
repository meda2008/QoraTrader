import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Table, 
  Button, 
  Space, 
  Modal, 
  Form, 
  Input, 
  InputNumber, 
  Select,
  Switch,
  message
} from 'antd';
import { RiskParams } from '../types/risk';
import { RiskRuleService } from '../services/riskRuleService';

const { Option } = Select;

const RiskConfig: React.FC = () => {
  const [riskRules, setRiskRules] = useState<RiskParams[]>([]);
  const [loading, setLoading] = useState(false);
  const [editingRule, setEditingRule] = useState<RiskParams | null>(null);
  const [isModalVisible, setIsModalVisible] = useState(false);

  // Fetch all risk rules
  useEffect(() => {
    fetchRiskRules();
  }, []);

  const fetchRiskRules = async () => {
    try {
      setLoading(true);
      const rules = await RiskRuleService.getRiskRules();
      setRiskRules(rules);
    } catch (error) {
      message.error('Failed to fetch risk rules');
    } finally {
      setLoading(false);
    }
  };

  const showModal = (rule?: RiskParams) => {
    setEditingRule(rule || null);
    setIsModalVisible(true);
  };

  const handleCancel = () => {
    setIsModalVisible(false);
    setEditingRule(null);
  };

  const handleSave = async (values: any) => {
    try {
      if (editingRule) {
        await RiskRuleService.updateRiskRule(editingRule.id, values);
        message.success('Risk rule updated successfully');
      } else {
        await RiskRuleService.createRiskRule(values);
        message.success('Risk rule created successfully');
      }
      handleCancel();
      fetchRiskRules();
    } catch (error) {
      message.error('Failed to save risk rule');
    }
  };

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
    },
    {
      title: 'Strategy',
      dataIndex: 'strategy_id',
      key: 'strategy_id',
      render: (strategyId: string) => strategyId || 'Global',
    },
    {
      title: 'Max Position Size',
      dataIndex: 'max_position_size',
      key: 'max_position_size',
      render: (value: number) => value.toLocaleString(),
    },
    {
      title: 'Max Order Size',
      dataIndex: 'max_order_size',
      key: 'max_order_size',
      render: (value: number) => value.toLocaleString(),
    },
    {
      title: 'Max Daily Loss',
      dataIndex: 'max_daily_loss',
      key: 'max_daily_loss',
      render: (value: number) => value.toLocaleString(),
    },
    {
      title: 'Max Drawdown',
      dataIndex: 'max_drawdown',
      key: 'max_drawdown',
      render: (value: number) => `${(value * 100).toFixed(2)}%`,
    },
    {
      title: 'Risk Level',
      dataIndex: 'risk_level',
      key: 'risk_level',
    },
    {
      title: 'Active',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (active: boolean) => active ? 'Yes' : 'No',
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: any, record: RiskParams) => (
        <Space>
          <Button 
            type="link" 
            onClick={() => showModal(record)}
          >
            Edit
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Card 
        title="Risk Configuration"
        extra={
          <Button 
            type="primary" 
            onClick={() => showModal()}
          >
            Add Risk Rule
          </Button>
        }
      >
        <Table 
          columns={columns}
          dataSource={riskRules}
          rowKey="id"
          loading={loading}
        />
      </Card>

      <Modal
        title={editingRule ? "Edit Risk Rule" : "Create Risk Rule"}
        open={isModalVisible}
        onCancel={handleCancel}
        footer={null}
      >
        <RiskRuleForm 
          initialData={editingRule} 
          onSave={handleSave} 
          onCancel={handleCancel}
        />
      </Modal>
    </div>
  );
};

// Form Component for Risk Rule
interface RiskRuleFormProps {
  initialData?: RiskParams | null;
  onSave: (values: any) => void;
  onCancel: () => void;
}

const RiskRuleForm: React.FC<RiskRuleFormProps> = ({ initialData, onSave, onCancel }) => {
  const [form] = Form.useForm();

  useEffect(() => {
    if (initialData) {
      form.setFieldsValue({
        ...initialData,
        max_drawdown: initialData.max_drawdown * 100, // Convert to percentage
      });
    } else {
      form.resetFields();
    }
  }, [initialData, form]);

  const onFinish = (values: any) => {
    // Convert percentage back to decimal
    values.max_drawdown = values.max_drawdown / 100;
    onSave(values);
  };

  return (
    <Form
      form={form}
      layout="vertical"
      onFinish={onFinish}
      initialValues={initialData}
    >
      <Form.Item
        name="strategy_id"
        label="Strategy (Leave blank for Global rule)"
      >
        <Input placeholder="Strategy ID (optional)" />
      </Form.Item>
      
      <Form.Item
        name="max_position_size"
        label="Max Position Size"
        rules={[{ required: true, message: 'Please enter max position size' }]}
      >
        <InputNumber 
          style={{ width: '100%' }} 
          placeholder="Max position size"
          min={0}
        />
      </Form.Item>

      <Form.Item
        name="max_order_size"
        label="Max Order Size"
        rules={[{ required: true, message: 'Please enter max order size' }]}
      >
        <InputNumber 
          style={{ width: '100%' }} 
          placeholder="Max order size"
          min={0}
        />
      </Form.Item>

      <Form.Item
        name="max_daily_loss"
        label="Max Daily Loss"
        rules={[{ required: true, message: 'Please enter max daily loss' }]}
      >
        <InputNumber 
          style={{ width: '100%' }} 
          placeholder="Max daily loss"
          min={0}
        />
      </Form.Item>

      <Form.Item
        name="max_drawdown"
        label="Max Drawdown (%)"
        rules={[{ required: true, message: 'Please enter max drawdown' }]}
      >
        <InputNumber 
          style={{ width: '100%' }} 
          placeholder="Max drawdown percentage"
          min={0}
          max={100}
          formatter={value => `${value}%`}
          parser={value => Number(value?.replace('%', ''))}
        />
      </Form.Item>

      <Form.Item
        name="risk_level"
        label="Risk Level"
        rules={[{ required: true, message: 'Please select risk level' }]}
      >
        <Select placeholder="Select risk level">
          <Option value="低">Low</Option>
          <Option value="中">Medium</Option>
          <Option value="高">High</Option>
        </Select>
      </Form.Item>

      <Form.Item
        name="is_active"
        label="Active"
        valuePropName="checked"
      >
        <Switch />
      </Form.Item>

      <Form.Item>
        <Space>
          <Button type="primary" htmlType="submit">
            Save
          </Button>
          <Button onClick={onCancel}>
            Cancel
          </Button>
        </Space>
      </Form.Item>
    </Form>
  );
};

export default RiskConfig;