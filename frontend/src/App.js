import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Layout, Alert } from 'antd';
import './App.css';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import PresentationList from './pages/PresentationList';
import PresentationDetail from './pages/PresentationDetail';
import CreatePresentation from './pages/CreatePresentation';

const { Content, Footer } = Layout;

function App() {
  return (
    <Router>
      <Layout style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
        <Navbar />
        <Content style={{ padding: '0', flex: 1 }}>
          <div style={{ maxWidth: '100%', margin: '0 auto' }}>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/dashboard" element={<PresentationList />} />
              <Route path="/presentation/:id" element={<PresentationDetail />} />
              <Route path="/create" element={<CreatePresentation />} />
              <Route path="*" element={
                <Alert
                  message="Page Not Found"
                  description="The page you're looking for doesn't exist."
                  type="error"
                  showIcon
                />
              } />
            </Routes>
          </div>
        </Content>
        <Footer style={{ textAlign: 'center', backgroundColor: '#f5f5f5', padding: '20px' }}>
          Powered by <span style={{ color: '#2f6690', fontWeight: '600' }}>Montlify</span>
        </Footer>
      </Layout>
    </Router>
  );
}

export default App;
