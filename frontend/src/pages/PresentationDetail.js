import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Spin, Button, Space, Carousel, Empty, Row, Col, Tag, Form, Input, Modal, message } from 'antd';
import { DeleteOutlined, EditOutlined, DownloadOutlined, SaveOutlined, CloseOutlined } from '@ant-design/icons';
import { presentationService, slideService } from '../services/api';

function PresentationDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [presentation, setPresentation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [currentSlide, setCurrentSlide] = useState(0);
  const [editMode, setEditMode] = useState(false);
  const [editingSlide, setEditingSlide] = useState(null);
  const [form] = Form.useForm();

  useEffect(() => {
    fetchPresentation();
  }, [id]);

  const fetchPresentation = async () => {
    try {
      setLoading(true);
      const response = await presentationService.getById(id);
      setPresentation(response.data);
    } catch (error) {
      console.error('Error fetching presentation:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this presentation?')) {
      try {
        await presentationService.delete(id);
        navigate('/');
      } catch (error) {
        console.error('Error deleting presentation:', error);
      }
    }
  };

  const handlePublish = async () => {
    try {
      await presentationService.publish(id);
      fetchPresentation();
    } catch (error) {
      console.error('Error publishing presentation:', error);
    }
  };

  const handleDownload = () => {
    if (!presentation || !presentation.slides) {
      message.error('No presentation data to download');
      return;
    }

    // Create a link to download PPTX
    const downloadUrl = `${process.env.REACT_APP_API_URL || 'http://localhost:8000/api'}/presentations/${id}/export_pptx/`;
    const token = process.env.REACT_APP_API_TOKEN || 'b1bf242b1c8a2b638e79f0b282599ffafea3faf3';
    
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = `${presentation.title.replace(/\s+/g, '_')}.pptx`;
    
    // Add auth header by using fetch
    fetch(downloadUrl, {
      headers: {
        'Authorization': `Token ${token}`
      }
    })
    .then(response => response.blob())
    .then(blob => {
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${presentation.title.replace(/\s+/g, '_')}.pptx`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      message.success('Presentation downloaded successfully!');
    })
    .catch(error => {
      console.error('Error downloading presentation:', error);
      message.error('Failed to download presentation');
    });
  };

  const handleEditSlide = (slide) => {
    setEditingSlide({ ...slide });
    // Handle both string and object bullets
    const bulletTexts = (slide.bullets || []).map(bullet => 
      typeof bullet === 'string' ? bullet : bullet.text || ''
    ).join('\n');
    
    form.setFieldsValue({
      title: slide.title,
      subtitle: slide.subtitle || '',
      content: slide.content || '',
      bullets: bulletTexts,
      speaker_notes: slide.speaker_notes || '',
    });
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
      message.success('Slide updated successfully!');
      setEditingSlide(null);
      fetchPresentation();
    } catch (error) {
      console.error('Error saving slide:', error);
      message.error('Failed to save slide');
    }
  };

  const handleCloseEditSlide = () => {
    setEditingSlide(null);
    form.resetFields();
  };

  if (loading) {
    return <Spin size="large" />;
  }

  if (!presentation) {
    return <Empty description="Presentation not found" />;
  }

  const slides = presentation.slides || [];

  return (
    <div>
      {/* Header Info */}
      <Card style={{ marginBottom: '20px' }}>
        <Row justify="space-between" align="middle">
          <Col>
            <h1>{presentation.title}</h1>
            <p style={{ color: '#666', marginBottom: '10px' }}>{presentation.description}</p>
            <div>
              <Tag color="blue">{presentation.tone}</Tag>
              <Tag color="green">{slides.length} Slides</Tag>
              <Tag color="cyan">{presentation.target_audience}</Tag>
              {presentation.is_published && <Tag color="red">Published</Tag>}
            </div>
          </Col>
          <Col>
            <Space>
              {editMode ? (
                <>
                  <Button type="primary" icon={<SaveOutlined />} onClick={handleSaveSlide}>Save Changes</Button>
                  <Button icon={<CloseOutlined />} onClick={() => setEditMode(false)}>Cancel Edit</Button>
                </>
              ) : (
                <>
                  <Button icon={<EditOutlined />} onClick={() => setEditMode(true)}>Edit Slides</Button>
                  <Button icon={<DownloadOutlined />} onClick={handleDownload}>Download PPTX</Button>
                  {!presentation.is_published && (
                    <Button type="primary" onClick={handlePublish}>Publish</Button>
                  )}
                  <Button danger icon={<DeleteOutlined />} onClick={handleDelete}>Delete</Button>
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
                          // Extract text from bullet (handle both string and object)
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
        <div style={{ maxHeight: '600px', overflowY: 'auto' }}>
          {slides.map((slide, index) => (
            <div key={slide.id} style={{ marginBottom: '20px', paddingBottom: '20px', borderBottom: '1px solid #f0f0f0' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
                <div style={{ display: 'flex', alignItems: 'center' }}>
                  <span style={{ fontSize: '18px', fontWeight: 'bold', marginRight: '10px' }}>
                    Slide {slide.slide_number}
                  </span>
                  <Tag>{slide.slide_type}</Tag>
                </div>
                {editMode && (
                  <Button size="small" type="primary" onClick={() => handleEditSlide(slide)}>
                    Edit Content
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
                      // Extract text from bullet (handle both string and object)
                      const bulletText = typeof bullet === 'string' ? bullet : bullet?.text || '';
                      const bulletObj = typeof bullet === 'object' && bullet !== null ? bullet : null;
                      
                      return (
                        <li key={idx} style={{ marginBottom: '8px' }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                            <span>{bulletText}</span>
                          </div>
                          {bulletObj && (bulletObj.emoji || bulletObj.icon || bulletObj.color) && (
                            <div style={{ fontSize: '12px', color: '#666', marginLeft: '20px' }}>
                              {bulletObj.emoji && <span>Emoji: {bulletObj.emoji} | </span>}
                              {bulletObj.icon && <span>Icon: {bulletObj.icon} | </span>}
                              {bulletObj.color && <span>Color: <span style={{ 
                                backgroundColor: bulletObj.color, 
                                padding: '2px 6px', 
                                borderRadius: '3px',
                                color: bulletObj.color === 'white' ? '#000' : '#fff'
                              }}>{bulletObj.color}</span></span>}
                            </div>
                          )}
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

              {slide.visuals && (Object.keys(slide.visuals).length > 0) && (
                <div style={{ marginTop: '10px', padding: '10px', background: '#f5f5f5', borderRadius: '4px' }}>
                  <strong>Visual Suggestions:</strong>
                  {slide.visuals.slide_icons && slide.visuals.slide_icons.length > 0 && (
                    <p style={{ fontSize: '12px', marginBottom: '4px' }}>Icons: {slide.visuals.slide_icons.join(', ')}</p>
                  )}
                  {slide.visuals.slide_symbols && slide.visuals.slide_symbols.length > 0 && (
                    <p style={{ fontSize: '12px', marginBottom: '4px' }}>Symbols: {slide.visuals.slide_symbols.join(', ')}</p>
                  )}
                  {slide.visuals.slide_image_ideas && slide.visuals.slide_image_ideas.length > 0 && (
                    <p style={{ fontSize: '12px', marginBottom: '0' }}>Images: {slide.visuals.slide_image_ideas.join(', ')}</p>
                  )}
                  {slide.visuals.icons && slide.visuals.icons.length > 0 && (
                    <p style={{ fontSize: '12px', marginBottom: '4px' }}>Icons: {slide.visuals.icons.join(', ')}</p>
                  )}
                  {slide.visuals.symbols && slide.visuals.symbols.length > 0 && (
                    <p style={{ fontSize: '12px', marginBottom: '4px' }}>Symbols: {slide.visuals.symbols.join(', ')}</p>
                  )}
                  {slide.visuals.image_ideas && slide.visuals.image_ideas.length > 0 && (
                    <p style={{ fontSize: '12px', marginBottom: '0' }}>Images: {slide.visuals.image_ideas.join(', ')}</p>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      </Card>

      {/* Edit Slide Modal */}
      <Modal
        title="Edit Slide Content"
        visible={editingSlide !== null}
        onOk={handleSaveSlide}
        onCancel={handleCloseEditSlide}
        width={700}
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
    </div>
  );
}

export default PresentationDetail;
