import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Layout } from 'antd';
import './App.css';
import Navbar from './components/Navbar';
import PresentationList from './pages/PresentationList';
import PresentationDetail from './pages/PresentationDetail';
import CreatePresentation from './pages/CreatePresentation';

const { Content } = Layout;

function App() {
  return (
    <Router>
      <Layout style={{ minHeight: '100vh' }}>
        <Navbar />
        <Content style={{ padding: '20px' }}>
          <Routes>
            <Route path="/" element={<PresentationList />} />
            <Route path="/presentation/:id" element={<PresentationDetail />} />
            <Route path="/create" element={<CreatePresentation />} />
          </Routes>
        </Content>
      </Layout>
    </Router>
  );
}

export default App;
