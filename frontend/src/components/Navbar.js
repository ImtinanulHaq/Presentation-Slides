import React from 'react';
import { Layout, Button, Space, Tooltip } from 'antd';
import { Link, useLocation } from 'react-router-dom';
import { PlusOutlined, HomeOutlined, UnorderedListOutlined } from '@ant-design/icons';
import '../styles/Navbar.css';

const { Header } = Layout;

function Navbar() {
  const location = useLocation();

  return (
    <Header className="navbar-header">
      <div className="navbar-container">
        <Link to="/" className="navbar-logo">
          <span className="logo-icon">📊</span>
          <span className="logo-text">Presentation Tools</span>
        </Link>
        
        <Space size="middle" className="navbar-menu">
          <Tooltip title="Go to Home">
            <Link to="/">
              <Button 
                type={location.pathname === '/' ? 'primary' : 'default'} 
                icon={<HomeOutlined />}
                className="nav-button"
              >
                Home
              </Button>
            </Link>
          </Tooltip>

          <Tooltip title="Go to Dashboard">
            <Link to="/dashboard">
              <Button 
                type={location.pathname === '/dashboard' ? 'primary' : 'default'} 
                icon={<UnorderedListOutlined />}
                className="nav-button"
              >
                Dashboard
              </Button>
            </Link>
          </Tooltip>
          
          <Tooltip title="Create a new presentation">
            <Link to="/create">
              <Button 
                type={location.pathname === '/create' ? 'primary' : 'default'} 
                icon={<PlusOutlined />}
                className="nav-button cta-nav-button"
              >
                New Presentation
              </Button>
            </Link>
          </Tooltip>
        </Space>
      </div>
    </Header>
  );
}

export default Navbar;
