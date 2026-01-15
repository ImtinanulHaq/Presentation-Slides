import React, { useEffect, useState } from 'react';
import { Card, Row, Col, Button, Empty, Spin, message, Space, Popconfirm, Tag, Statistic, Alert } from 'antd';
import { Link } from 'react-router-dom';
import { PlusOutlined, DeleteOutlined, DeleteFilled } from '@ant-design/icons';
import { presentationService } from '../services/api';
import '../styles/PresentationList.css';

function PresentationList() {
  const [presentations, setPresentations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [deletingAll, setDeletingAll] = useState(false);

  useEffect(() => {
    fetchPresentations();
  }, []);

  const fetchPresentations = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await presentationService.getAll();
      const data = response.data?.results || response.data || [];
      setPresentations(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Error fetching presentations:', error);
      let errorMsg = 'Error loading presentations';
      
      if (error.response?.status === 401) {
        errorMsg = 'Authentication failed. Please check your API token.';
      } else if (error.response?.status === 403) {
        errorMsg = 'Permission denied. You do not have access to presentations.';
      } else if (error.code === 'ECONNABORTED' || !error.response) {
        errorMsg = 'Cannot connect to backend. Make sure Django is running on port 8000.';
      }
      
      setError(errorMsg);
      setPresentations([]);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id, title) => {
    try {
      await presentationService.delete(id);
      message.success(`"${title}" deleted successfully`);
      fetchPresentations();
    } catch (error) {
      console.error('Error deleting presentation:', error);
      message.error('Failed to delete presentation');
    }
  };

  const handleDeleteAll = async () => {
    try {
      setDeletingAll(true);
      
      const deletePromises = presentations.map(pres =>
        presentationService.delete(pres.id).catch(err => {
          console.error(`Failed to delete presentation ${pres.id}:`, err);
          return null;
        })
      );
      
      await Promise.all(deletePromises);
      
      message.success(`All ${presentations.length} presentations deleted successfully!`);
      setPresentations([]);
    } catch (error) {
      console.error('Error deleting all presentations:', error);
      message.error('Failed to delete some presentations');
      fetchPresentations();
    } finally {
      setDeletingAll(false);
    }
  };

  if (loading) {
    return <Spin size="large" tip="Loading presentations..." />;
  }

  return (
    <div className="dashboard-container">
      <Card className="dashboard-header-card">
        <Row justify="space-between" align="middle">
          <Col xs={24} sm={12}>
            <h1 className="dashboard-title">📊 Dashboard</h1>
            <p className="dashboard-subtitle">Manage and organize your presentation projects</p>
          </Col>
          <Col xs={24} sm={12} style={{ textAlign: 'right' }}>
            <Link to="/create">
              <Button type="primary" size="large" icon={<PlusOutlined />} className="create-button">
                Create New Presentation
              </Button>
            </Link>
          </Col>
        </Row>
      </Card>

      {error && (
        <Alert
          message="Error Loading Presentations"
          description={error}
          type="error"
          showIcon
          closable
          style={{ marginBottom: '20px' }}
        />
      )}

      {presentations.length === 0 ? (
        <Card className="empty-card">
          <Empty
            description="No presentations yet"
            style={{ marginTop: '50px', marginBottom: '50px' }}
          >
            <Link to="/create">
              <Button type="primary" size="large" icon={<PlusOutlined />} className="create-button">
                Create Your First Presentation
              </Button>
            </Link>
          </Empty>
        </Card>
      ) : (
        <>
          <Card className="statistics-card">
            <Row gutter={[16, 16]}>
              <Col xs={24} sm={8}>
                <Statistic 
                  title="Total Presentations" 
                  value={presentations.length}
                  valueStyle={{ color: '#2f6690', fontSize: '2.5rem' }}
                />
              </Col>
              <Col xs={24} sm={8}>
                <Statistic 
                  title="Total Slides" 
                  value={presentations.reduce((sum, p) => sum + (p.total_slides || p.slides?.length || 0), 0)}
                  valueStyle={{ color: '#81c3d7', fontSize: '2.5rem' }}
                />
              </Col>
              <Col xs={24} sm={8} style={{ textAlign: 'right' }}>
                {presentations.length > 0 && (
                  <Popconfirm
                    title="Delete All Presentations"
                    description={`Are you sure you want to permanently delete all ${presentations.length} presentations? This action cannot be undone.`}
                    onConfirm={handleDeleteAll}
                    okText="Yes, Delete All"
                    cancelText="Cancel"
                    okButtonProps={{ danger: true }}
                    placement="topRight"
                  >
                    <Button 
                      danger 
                      size="large" 
                      icon={<DeleteFilled />}
                      loading={deletingAll}
                      className="delete-all-button"
                    >
                      Delete All
                    </Button>
                  </Popconfirm>
                )}
              </Col>
            </Row>
          </Card>

          <div className="presentations-grid">
            <Row gutter={[20, 20]}>
              {presentations.map((presentation) => (
                <Col xs={24} sm={12} md={8} key={presentation.id}>
                  <Card
                    hoverable
                    className="presentation-card"
                    cover={
                      <div className="presentation-cover">
                        <div className="slide-count">
                          {presentation.total_slides || presentation.slides?.length || 0} Slides
                        </div>
                      </div>
                    }
                  >
                    <div className="card-content">
                      <h3 className="presentation-title">{presentation.title}</h3>
                      <p className="presentation-topic">
                        {presentation.topic || 'No topic'}
                      </p>
                      
                      <div className="presentation-tags">
                        <Space size="small" wrap>
                          <Tag className="tag-tone">{presentation.tone || 'N/A'}</Tag>
                          <Tag className="tag-audience">{presentation.target_audience || 'N/A'}</Tag>
                          {presentation.subject && presentation.subject !== 'general' && (
                            <Tag className="tag-subject">{presentation.subject}</Tag>
                          )}
                          {presentation.is_published && <Tag color="red">Published</Tag>}
                        </Space>
                      </div>

                      <div className="card-actions">
                        <Link to={`/presentation/${presentation.id}`}>
                          <Button type="primary" block className="view-button">
                            View Presentation
                          </Button>
                        </Link>
                        <Popconfirm
                          title="Delete Presentation"
                          description={`Are you sure you want to delete "${presentation.title}"?`}
                          onConfirm={() => handleDelete(presentation.id, presentation.title)}
                          okText="Yes"
                          cancelText="No"
                          okButtonProps={{ danger: true }}
                        >
                          <Button danger block icon={<DeleteOutlined />} className="delete-button">
                            Delete
                          </Button>
                        </Popconfirm>
                      </div>
                    </div>
                  </Card>
                </Col>
              ))}
            </Row>
          </div>
        </>
      )}
    </div>
  );
}

export default PresentationList;
