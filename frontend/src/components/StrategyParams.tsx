import React, { useState, useEffect } from 'react';
import { Card, Form, Input, Button, Slider, Switch, InputNumber, message } from 'antd';
import { ReloadOutlined, SaveOutlined } from '@ant-design/icons';
import { getStrategyParams, updateStrategyParams } from '../services/strategyService';

const { Item } = Form;

interface StrategyParamsProps {
  strategyId: string;
}

const StrategyParams: React.FC<StrategyParamsProps> = ({ strategyId }) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState<boolean>(false);
  const [params, setParams] = useState<Record<string, any>>({});

  useEffect(() => {
    fetchParams();
  }, [strategyId]);

  const fetchParams = async () => {
    try {
      setLoading(true);
      const response = await getStrategyParams(strategyId);
      setParams(response.data);
      form.setFieldsValue(response.data);
    } catch (error) {
      console.error('Failed to fetch strategy params:', error);
      message.error('获取策略参数失败');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (values: any) => {
    try {
      setLoading(true);
      await updateStrategyParams(strategyId, values);
      message.success('策略参数更新成功');
    } catch (error) {
      console.error('Failed to update strategy params:', error);
      message.error('更新策略参数失败');
    } finally {
      setLoading(false);
    }
  };

  if (!params || Object.keys(params).length === 0) {
    return (
      <Card title="策略参数">
        <p>暂无策略参数</p>
      </Card>
    );
  }

  // 根据参数类型渲染不同的输入组件
  const renderParamField = (key: string, value: any) => {
    const paramType = typeof value;
    
    switch (paramType) {
      case 'boolean':
        return <Switch />;
      case 'number':
        if (Number.isInteger(value)) {
          return <InputNumber min={0} max={100000} step={1} />;
        } else {
          return <InputNumber min={0} max={1} step={0.01} />;
        }
      case 'string':
        if (value.length > 50) {
          return <Input.TextArea rows={4} />;
        } else {
          return <Input />;
        }
      default:
        return <Input />;
    }
  };

  return (
    <Card 
      title="策略参数调整" 
      extra={
        <Button 
          icon={<ReloadOutlined />} 
          onClick={fetchParams}
          loading={loading}
        >
          刷新
        </Button>
      }
    >
      <Form
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
      >
        {Object.keys(params).map(key => (
          <Item
            key={key}
            name={key}
            label={key}
            initialValue={params[key]}
          >
            {renderParamField(key, params[key])}
          </Item>
        ))}
        
        <Item>
          <Button 
            type="primary" 
            htmlType="submit" 
            icon={<SaveOutlined />}
            loading={loading}
          >
            保存参数
          </Button>
        </Item>
      </Form>
    </Card>
  );
};

export default StrategyParams;