import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Spin, Button, Space, Carousel, Empty, Row, Col, Tag, Form, Input, Modal, message, Alert, Popconfirm, Select } from 'antd';
import { DeleteOutlined, EditOutlined, DownloadOutlined, SaveOutlined, CloseOutlined } from '@ant-design/icons';
import { presentationService, slideService } from '../services/api';
import ScriptGenerationModal from '../components/ScriptGenerationModal';

function PresentationDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [presentation, setPresentation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentSlide, setCurrentSlide] = useState(0);
  const [editMode, setEditMode] = useState(false);
  const [editingSlide, setEditingSlide] = useState(null);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [isScriptModalVisible, setIsScriptModalVisible] = useState(false);
  const [downloadRatio, setDownloadRatio] = useState('16:9');  // Default slide ratio
  const [form] = Form.useForm();

  useEffect(() => {
    fetchPresentation();
  }, [id]);

  // Suppress ResizeObserver error from Ant Design Carousel
  useEffect(() => {
    const handleError = (event) => {
      if (event.message === 'ResizeObserver loop completed with undelivered notifications.') {
        event.stopImmediatePropagation();
      }
    };
    window.addEventListener('error', handleError);
    return () => window.removeEventListener('error', handleError);
  }, []);

  const fetchPresentation = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await presentationService.getById(id);
      setPresentation(response.data);
    } catch (error) {
      console.error('Error fetching presentation:', error);
      let errorMsg = 'Error loading presentation';
      
      if (error.response?.status === 404) {
        errorMsg = 'Presentation not found';
      } else if (error.response?.status === 401) {
        errorMsg = 'Authentication failed. Please refresh the page.';
      } else if (!error.response) {
        errorMsg = 'Cannot connect to backend. Make sure Django is running.';
      }
      
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    try {
      await presentationService.delete(id);
      message.success('Presentation deleted');
      navigate('/');
    } catch (error) {
      console.error('Error deleting presentation:', error);
      message.error('Failed to delete presentation');
    }
  };

  const handlePublish = async () => {
    try {
      await presentationService.publish(id);
      message.success('Presentation published');
      fetchPresentation();
    } catch (error) {
      console.error('Error publishing presentation:', error);
      message.error('Failed to publish presentation');
    }
  };

  const handleDownload = async () => {
    try {
      if (!presentation) {
        message.error('No presentation data to download');
        return;
      }

      const token = process.env.REACT_APP_API_TOKEN || 'b1bf242b1c8a2b638e79f0b282599ffafea3faf3';
      const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
      const downloadUrl = `${apiUrl}/presentations/${id}/export_pptx/?slide_ratio=${downloadRatio}`;
      
      const response = await fetch(downloadUrl, {
        headers: {
          'Authorization': `Token ${token}`
        }
      });

      if (!response.ok) {
        throw new Error(`Download failed with status ${response.status}`);
      }

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${presentation.title.replace(/\s+/g, '_')}_${downloadRatio.replace(':', '')}.pptx`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      message.success(`Presentation downloaded successfully (${downloadRatio})`);
    } catch (error) {
      console.error('Error downloading presentation:', error);
      message.error('Failed to download presentation. Make sure backend supports PPTX export.');
    }
  };

  const handleEditSlide = (slide) => {
    setEditingSlide({ ...slide });
    const bulletTexts = (slide.bullets || []).map(bullet => 
      typeof bullet === 'string' ? bullet : bullet?.text || ''
    ).join('\n');
    
    form.setFieldsValue({
      title: slide.title,
      subtitle: slide.subtitle || '',
      content: slide.content || '',
      bullets: bulletTexts,
      speaker_notes: slide.speaker_notes || '',
    });
    setIsModalVisible(true);
  };

  const handleSaveSlide = async () => {
    try {
      const values = await form.validateFields();
      const updatedSlide = {
        ...editingSlide,
        title: values.title,
        subtitle: values.subtitle,
        content: values.content,
        bullets: values.bullets ? values.bullets.split('\n').map(b => b.trim()).filter(b => b) : [],
        speaker_notes: values.speaker_notes,
      };

      await slideService.update(editingSlide.id, updatedSlide);
      message.success('Slide updated');
      setIsModalVisible(false);
      setEditingSlide(null);
      form.resetFields();
      fetchPresentation();
    } catch (error) {
      console.error('Error saving slide:', error);
      message.error('Failed to save slide');
    }
  };

  const handleCloseEditSlide = () => {
    setIsModalVisible(false);
    setEditingSlide(null);
    form.resetFields();
  };

  if (loading) {
    return <Spin size="large" tip="Loading presentation..." />;
  }

  if (error) {
    return (
      <Card>
        <Alert
          message="Error Loading Presentation"
          description={error}
          type="error"
          showIcon
        />
        <Button onClick={() => navigate('/')} style={{ marginTop: '20px' }}>
          Back to List
        </Button>
      </Card>
    );
  }

  if (!presentation) {
    return (
      <Card>
        <Empty description="Presentation not found" />
        <Button onClick={() => navigate('/')} style={{ marginTop: '20px' }}>
          Back to List
        </Button>
      </Card>
    );
  }

  const slides = presentation.slides || [];

  return (
    <div>
      {/* Header Info */}
      <Card style={{ marginBottom: '20px' }}>
        <Row justify="space-between" align="middle">
          <Col span={12}>
            <h1 style={{ marginBottom: '8px' }}>{presentation.title}</h1>
            <p style={{ color: '#666', marginBottom: '10px' }}>{presentation.topic}</p>
            <Space wrap>
              <Tag color="blue">{presentation.tone || 'N/A'}</Tag>
              <Tag color="green">{slides.length} Slides</Tag>
              <Tag color="cyan">{presentation.target_audience}</Tag>
              {presentation.subject && presentation.subject !== 'general' && (
                <Tag color="purple">{presentation.subject}</Tag>
              )}
              {presentation.is_published && <Tag color="red">Published</Tag>}
            </Space>
            {(presentation.title_font || presentation.heading_font || presentation.content_font) && (
              <p style={{ fontSize: '12px', color: '#999', marginTop: '10px' }}>
                🎨 Fonts: Title: {presentation.title_font} | Heading: {presentation.heading_font} | Content: {presentation.content_font}
              </p>
            )}
          </Col>
          <Col span={12} style={{ textAlign: 'right' }}>
            <Space direction="vertical" style={{ width: '100%' }}>
              {editMode ? (
                <>
                  <Button onClick={() => setEditMode(false)}>Done Editing</Button>
                </>
              ) : (
                <>
                  <Button 
                    type="primary" 
                    onClick={() => setIsScriptModalVisible(true)}
                    style={{ backgroundColor: '#f97316', borderColor: '#f97316' }}
                  >
                    🎤 Generate Script
                  </Button>
                  <Space>
                    <Select 
                      value={downloadRatio}
                      onChange={setDownloadRatio}
                      style={{ width: 170 }}
                    >
                      <Select.Option value="16:9">🖥️ Widescreen (16:9)</Select.Option>
                      <Select.Option value="4:3">📺 Standard (4:3)</Select.Option>
                      <Select.Option value="1:1">□ Square (1:1)</Select.Option>
                      <Select.Option value="2:3">📱 Portrait (2:3)</Select.Option>
                    </Select>
                    <Button type="primary" icon={<DownloadOutlined />} onClick={handleDownload}>
                      Download PPTX
                    </Button>
                  </Space>
                  {!presentation.is_published && (
                    <Button type="primary" onClick={handlePublish}>
                      Publish
                    </Button>
                  )}
                  <Popconfirm
                    title="Delete Presentation"
                    description="Are you sure you want to delete this presentation?"
                    onConfirm={handleDelete}
                    okText="Yes"
                    cancelText="No"
                    okButtonProps={{ danger: true }}
                  >
                    <Button danger icon={<DeleteOutlined />}>
                      Delete
                    </Button>
                  </Popconfirm>
                </>
              )}
            </Space>
          </Col>
        </Row>
      </Card>

      {/* Slides Carousel */}
      {slides.length > 0 ? (
        <div>
          <Carousel 
            autoplay={false}
            onChange={(current) => setCurrentSlide(current)}
            style={{ marginBottom: '20px' }}
          >
            {slides.map((slide) => (
              <div key={slide.id}>
                <Card
                  style={{
                    background: slide.slide_type === 'title' ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' : '#fff',
                    color: slide.slide_type === 'title' ? 'white' : 'black',
                    minHeight: '500px',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'center',
                    padding: '40px',
                  }}
                >
                  <div style={{ textAlign: 'center' }}>
                    <h2 style={{ marginBottom: '10px' }}>{slide.title}</h2>
                    {slide.subtitle && (
                      <h4 style={{ marginBottom: '30px', opacity: 0.9 }}>{slide.subtitle}</h4>
                    )}

                    {slide.bullets && slide.bullets.length > 0 && (
                      <ul style={{ textAlign: 'left', display: 'inline-block', marginTop: '20px' }}>
                        {slide.bullets.map((bullet, idx) => {
                          const bulletText = typeof bullet === 'string' ? bullet : bullet?.text || '';
                          const bulletObj = typeof bullet === 'object' && bullet !== null ? bullet : null;
                          
                          return (
                            <li key={idx} style={{ marginBottom: '10px', fontSize: '16px' }}>
                              {bulletObj?.emoji && <span style={{ marginRight: '8px' }}>{bulletObj.emoji}</span>}
                              {bulletText}
                            </li>
                          );
                        })}
                      </ul>
                    )}
                  </div>
                </Card>
              </div>
            ))}
          </Carousel>

          <Card>
            <p style={{ textAlign: 'center' }}>
              Slide {currentSlide + 1} of {slides.length}
            </p>
          </Card>
        </div>
      ) : (
        <Card>
          <Empty description="No slides in this presentation" />
        </Card>
      )}

      {/* Slides Details */}
      <Card title="Slide Details" style={{ marginTop: '30px' }}>
        <Button 
          type={editMode ? "danger" : "primary"} 
          onClick={() => setEditMode(!editMode)}
          style={{ marginBottom: '20px' }}
          icon={editMode ? <CloseOutlined /> : <EditOutlined />}
        >
          {editMode ? 'Cancel Editing' : 'Edit Slides'}
        </Button>
        
        <div style={{ maxHeight: '600px', overflowY: 'auto' }}>
          {slides.map((slide, index) => (
            <div key={slide.id} style={{ marginBottom: '20px', paddingBottom: '20px', borderBottom: '1px solid #f0f0f0' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
                <div>
                  <span style={{ fontSize: '18px', fontWeight: 'bold', marginRight: '10px' }}>
                    Slide {slide.slide_number}
                  </span>
                  <Tag>{slide.slide_type}</Tag>
                </div>
                {editMode && (
                  <Button size="small" type="primary" onClick={() => handleEditSlide(slide)}>
                    Edit
                  </Button>
                )}
              </div>
              <h4>{slide.title}</h4>
              {slide.subtitle && <p style={{ color: '#666' }}>{slide.subtitle}</p>}
              
              {slide.bullets && slide.bullets.length > 0 && (
                <div style={{ marginTop: '15px' }}>
                  <strong>Bullets:</strong>
                  <ul>
                    {slide.bullets.map((bullet, idx) => {
                      const bulletText = typeof bullet === 'string' ? bullet : bullet?.text || '';
                      return (
                        <li key={idx} style={{ marginBottom: '8px' }}>
                          {bulletText}
                        </li>
                      );
                    })}
                  </ul>
                </div>
              )}

              {slide.speaker_notes && (
                <div style={{ background: '#f5f5f5', padding: '10px', marginTop: '10px', borderRadius: '4px' }}>
                  <strong>Speaker Notes:</strong> {slide.speaker_notes}
                </div>
              )}
            </div>
          ))}
        </div>
      </Card>

      {/* Edit Slide Modal */}
      <Modal
        title="Edit Slide Content"
        open={isModalVisible}
        onOk={handleSaveSlide}
        onCancel={handleCloseEditSlide}
        width={700}
        okText="Save"
        cancelText="Cancel"
      >
        {editingSlide && (
          <Form form={form} layout="vertical">
            <Form.Item
              name="title"
              label="Slide Title"
              rules={[{ required: true, message: 'Please enter slide title' }]}
            >
              <Input placeholder="Slide title" />
            </Form.Item>

            <Form.Item
              name="subtitle"
              label="Subtitle (Optional)"
            >
              <Input placeholder="Subtitle" />
            </Form.Item>

            <Form.Item
              name="content"
              label="Content (Optional)"
            >
              <Input.TextArea placeholder="Main content" rows={3} />
            </Form.Item>

            <Form.Item
              name="bullets"
              label="Bullet Points (One per line)"
            >
              <Input.TextArea 
                placeholder="Bullet point 1&#10;Bullet point 2&#10;Bullet point 3" 
                rows={4}
              />
            </Form.Item>

            <Form.Item
              name="speaker_notes"
              label="Speaker Notes (Optional)"
            >
              <Input.TextArea placeholder="Notes for the presenter" rows={3} />
            </Form.Item>
          </Form>
        )}
      </Modal>

      {/* Script Generation Modal */}
      <ScriptGenerationModal 
        visible={isScriptModalVisible}
        onCancel={() => setIsScriptModalVisible(false)}
        presentation={presentation}
        onScriptGenerated={() => {
          setIsScriptModalVisible(false);
        }}
      />
    </div>
  );
}

export default PresentationDetail;
