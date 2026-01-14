import React from 'react';
import { Layout, Button, Space } from 'antd';
import { Link } from 'react-router-dom';
import { PlusOutlined } from '@ant-design/icons';

const { Header } = Layout;

function Navbar() {
  return (
    <Header style={{ background: '#001529', color: '#fff' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Link to="/" style={{ color: 'white', fontSize: '20px', fontWeight: 'bold' }}>
          📊 Presentation Tools
        </Link>
        <Space>
          <Link to="/">
            <Button type="primary">Dashboard</Button>
          </Link>
          <Link to="/create">
            <Button type="primary" icon={<PlusOutlined />}>
              New Presentation
            </Button>
          </Link>
        </Space>
      </div>
    </Header>
  );
}

export default Navbar;
