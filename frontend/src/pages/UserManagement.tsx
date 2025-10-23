import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Space, Modal, Form, Input, Select, Switch, message, Tag } from 'antd';
import { UserAddOutlined, EditOutlined, DeleteOutlined, ReloadOutlined } from '@ant-design/icons';
import { getUsers, createUser, updateUser, deleteUser } from '../services/userService';
import { User } from '../types/user';

const { Item } = Form;
const { Option } = Select;

const UserManagement: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [modalVisible, setModalVisible] = useState<boolean>(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [form] = Form.useForm();

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const response = await getUsers();
      setUsers(response.data);
    } catch (error) {
      console.error('Failed to fetch users:', error);
      message.error('获取用户列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateUser = () => {
    setEditingUser(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEditUser = (user: User) => {
    setEditingUser(user);
    form.setFieldsValue({
      username: user.username,
      email: user.email,
      role: user.role,
      is_active: user.is_active,
    });
    setModalVisible(true);
  };

  const handleDeleteUser = async (userId: string) => {
    Modal.confirm({
      title: '确认删除',
      content: '您确定要删除这个用户吗？此操作不可恢复。',
      onOk: async () => {
        try {
          await deleteUser(userId);
          message.success('用户删除成功');
          fetchUsers(); // 重新获取用户列表
        } catch (error) {
          console.error('Failed to delete user:', error);
          message.error('用户删除失败');
        }
      },
    });
  };

  const handleSubmit = async (values: any) => {
    try {
      if (editingUser) {
        // 更新用户
        await updateUser(editingUser.id, {
          ...values,
          id: editingUser.id, // 确保ID不变
        });
        message.success('用户更新成功');
      } else {
        // 创建新用户
        await createUser(values);
        message.success('用户创建成功');
      }
      
      setModalVisible(false);
      fetchUsers(); // 重新获取用户列表
    } catch (error) {
      console.error('Failed to save user:', error);
      message.error(editingUser ? '用户更新失败' : '用户创建失败');
    }
  };

  const getUserRoleTag = (role: string) => {
    switch (role) {
      case 'admin':
        return <Tag color="red">管理员</Tag>;
      case 'strategist':
        return <Tag color="blue">策略师</Tag>;
      case 'trader':
        return <Tag color="green">交易员</Tag>;
      default:
        return <Tag>{role}</Tag>;
    }
  };

  const columns = [
    {
      title: '用户名',
      dataIndex: 'username',
      key: 'username',
    },
    {
      title: '邮箱',
      dataIndex: 'email',
      key: 'email',
    },
    {
      title: '角色',
      dataIndex: 'role',
      key: 'role',
      render: (role: string) => getUserRoleTag(role),
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (isActive: boolean) => (
        <Tag color={isActive ? 'green' : 'default'}>
          {isActive ? '激活' : '未激活'}
        </Tag>
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (text: string) => new Date(text).toLocaleString(),
    },
    {
      title: '操作',
      key: 'actions',
      render: (text: any, record: User) => (
        <Space>
          <Button 
            type="link" 
            icon={<EditOutlined />} 
            onClick={() => handleEditUser(record)}
          >
            编辑
          </Button>
          <Button 
            type="link" 
            danger
            icon={<DeleteOutlined />} 
            onClick={() => handleDeleteUser(record.id)}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <Button 
          type="primary" 
          icon={<UserAddOutlined />} 
          onClick={handleCreateUser}
        >
          新增用户
        </Button>
        <Button 
          icon={<ReloadOutlined />} 
          onClick={fetchUsers}
          loading={loading}
        >
          刷新
        </Button>
      </Space>

      <Card>
        <Table
          dataSource={users}
          columns={columns}
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      <Modal
        title={editingUser ? '编辑用户' : '新增用户'}
        visible={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        destroyOnClose
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Item
            name="username"
            label="用户名"
            rules={[{ required: true, message: '请输入用户名' }]}
          >
            <Input placeholder="请输入用户名" />
          </Item>
          
          <Item
            name="email"
            label="邮箱"
            rules={[
              { required: true, message: '请输入邮箱' },
              { type: 'email', message: '请输入有效的邮箱地址' },
            ]}
          >
            <Input placeholder="请输入邮箱" />
          </Item>
          
          <Item
            name="role"
            label="角色"
            rules={[{ required: true, message: '请选择角色' }]}
          >
            <Select placeholder="请选择角色">
              <Option value="admin">管理员</Option>
              <Option value="strategist">策略师</Option>
              <Option value="trader">交易员</Option>
            </Select>
          </Item>
          
          <Item
            name="is_active"
            label="激活状态"
            valuePropName="checked"
          >
            <Switch />
          </Item>
          
          {editingUser && (
            <Item
              name="password"
              label="密码"
              tooltip="仅在创建用户或修改密码时填写"
            >
              <Input.Password placeholder="留空则不修改密码" />
            </Item>
          )}
          
          {!editingUser && (
            <Item
              name="password"
              label="密码"
              rules={[{ required: true, message: '请输入密码' }]}
            >
              <Input.Password placeholder="请输入密码" />
            </Item>
          )}
          
          <Item>
            <Space>
              <Button type="primary" htmlType="submit">
                {editingUser ? '更新' : '创建'}
              </Button>
              <Button onClick={() => setModalVisible(false)}>
                取消
              </Button>
            </Space>
          </Item>
        </Form>
      </Modal>
    </div>
  );
};

export default UserManagement;