import React, { useState } from 'react';
import { Form, Input, Button, Card, message, Select, Spin, Alert, Divider, Row, Col, Checkbox } from 'antd';
import { useNavigate } from 'react-router-dom';
import { PlusOutlined } from '@ant-design/icons';
import { presentationService } from '../services/api';
import '../styles/CreatePresentation.css';

const { TextArea } = Input;
const { Option } = Select;

// Professional Template Definitions
const TEMPLATES = {
  warm_blue: {
    name: 'Warm Blue',
    description: 'Professional template with warm blue palette',
    primaryColor: '#2f6690',
    accentColor: '#81c3d7',
    backgroundColor: '#2f6690',
    textColor: '#d9dcd6',
    secondaryColor: '#3a7ca5',
    accentLight: '#81c3d7',
  },
  rose_elegance: {
    name: 'Rose Elegance',
    description: 'Premium professional template with rose gold palette',
    primaryColor: '#9d8189',
    accentColor: '#f4acb7',
    backgroundColor: '#9d8189',
    textColor: '#ffe5d9',
    secondaryColor: '#d8e2dc',
    accentLight: '#ffcad4',
  },
  warm_spectrum: {
    name: 'Warm Spectrum',
    description: 'Modern vibrant template with ocean-to-sunset gradient',
    primaryColor: '#005f73',
    accentColor: '#ee9b00',
    backgroundColor: '#005f73',
    textColor: '#e9d8a6',
    secondaryColor: '#0a9396',
    accentLight: '#94d2bd',
  },
};

// Professional Template Selector Component
function TemplateSelector({ value, onChange }) {
  return (
    <div className="template-selector-grid">
      {Object.entries(TEMPLATES).map(([key, template]) => (
        <div
          key={key}
          onClick={() => onChange(key)}
          className={`template-card ${value === key ? 'selected' : ''}`}
        >
          {/* Color Preview */}
          <div className="template-color-preview">
            <div 
              style={{ backgroundColor: template.primaryColor }}
              className="color-swatch"
              title={template.primaryColor}
            />
            <div 
              style={{ backgroundColor: template.accentColor }}
              className="color-swatch"
              title={template.accentColor}
            />
          </div>

          {/* Template Info */}
          <h4 className="template-name">{template.name}</h4>
          <p className="template-description">{template.description}</p>

          {/* Selected Badge */}
          {value === key && (
            <div className="template-selected-badge">✓ Selected</div>
          )}
        </div>
      ))}
    </div>
  );
}

function CreatePresentation() {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState('warm_blue');
  const [showTemplateSelector, setShowTemplateSelector] = useState(false);
  const [step, setStep] = useState(1);
  const [generatedPresentation, setGeneratedPresentation] = useState(null);
  const navigate = useNavigate();

  const onGeneratePresentation = async (values) => {
    try {
      setLoading(true);
      
      const requiredFields = {
        topic: 'Topic',
        raw_content: 'Raw Content',
        target_audience: 'Target Audience',
        tone: 'Presentation Tone'
      };
      
      const missingFields = [];
      for (const [field, label] of Object.entries(requiredFields)) {
        if (!values[field]) {
          missingFields.push(label);
        }
      }
      
      if (missingFields.length > 0) {
        message.error(`Missing required fields: ${missingFields.join(', ')}`);
        setLoading(false);
        return;
      }
      
      const cleanValues = {
        topic: values.topic?.trim(),
        raw_content: values.raw_content?.trim(),
        target_audience: values.target_audience?.trim(),
        tone: values.tone,
        subject: values.subject || 'general',
        slide_ratio: values.slide_ratio || '16:9',
        bullet_style: values.bullet_style || 'numbered',
        presentation_title: values.presentation_title?.trim() || '',
        num_slides: values.num_slides ? parseInt(values.num_slides) : null,
        enable_visuals: values.enable_visuals === true,
        template: selectedTemplate
      };
      
      const response = await presentationService.generate(cleanValues);
      
      message.success('Presentation generated successfully!');
      setGeneratedPresentation(response.data);
      setStep(2);
    } catch (error) {
      let errorMessage = 'Error generating presentation';
      
      if (error.response?.status === 401) {
        errorMessage = 'Authentication failed: Invalid or expired token.';
      } else if (error.response?.status === 403) {
        errorMessage = 'Permission denied: You do not have access to this resource.';
      } else if (error.response?.status === 400) {
        const backendError = error.response.data;
        if (typeof backendError === 'object') {
          const errors = [];
          Object.entries(backendError).forEach(([field, messages]) => {
            if (Array.isArray(messages)) {
              errors.push(`${field}: ${messages.join(', ')}`);
            } else {
              errors.push(`${field}: ${messages}`);
            }
          });
          errorMessage = `Validation error: ${errors.join(' | ')}`;
        }
      } else if (error.response?.status === 500) {
        errorMessage = 'Server error: The presentation generation failed.';
      } else if (error.code === 'ERR_NETWORK' || error.message === 'Network Error') {
        errorMessage = 'Network error: Cannot connect to backend.';
      }
      
      message.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const onConfirmPresentation = async () => {
    try {
      message.success('Presentation saved!');
      navigate(`/presentation/${generatedPresentation.id}`);
    } catch (error) {
      message.error('Error saving presentation');
    }
  };

  const onEditPresentation = () => {
    setStep(1);
    setGeneratedPresentation(null);
  };

  if (loading) {
    return (
      <Spin size="large" spinning={true} fullscreen tip="Generating your presentation..." />
    );
  }

  if (step === 2 && generatedPresentation) {
    return (
      <div className="create-presentation-container">
        <Card className="preview-header-card">
          <h1>✨ Presentation Preview</h1>
          <Alert
            message="Your presentation has been generated!"
            description={`${generatedPresentation.total_slides} slides created based on your content`}
            type="success"
            showIcon
            style={{ marginBottom: '20px' }}
          />
        </Card>

        <Row gutter={16}>
          <Col xs={24} md={12}>
            <Card title="Presentation Details" className="preview-card">
              <p><strong>Title:</strong> {generatedPresentation.title}</p>
              <p><strong>Topic:</strong> {generatedPresentation.topic}</p>
              <p><strong>Audience:</strong> {generatedPresentation.target_audience}</p>
              <p><strong>Tone:</strong> {generatedPresentation.tone}</p>
              <p><strong>Subject:</strong> {generatedPresentation.subject || 'General'}</p>
              <p><strong>Total Slides:</strong> {generatedPresentation.total_slides}</p>
            </Card>
          </Col>

          <Col xs={24} md={12}>
            <Card title="Content Summary" className="preview-card">
              <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
                <p>{generatedPresentation.raw_content.substring(0, 200)}...</p>
              </div>
            </Card>
          </Col>
        </Row>

        <Card title="Generated Slides" className="slides-preview-card" style={{ marginTop: '20px', marginBottom: '20px' }}>
          <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
            {generatedPresentation.slides && generatedPresentation.slides.map((slide) => (
              <div key={slide.id} style={{ marginBottom: '15px', paddingBottom: '15px', borderBottom: '1px solid #f0f0f0' }}>
                <strong>Slide {slide.slide_number}: {slide.title}</strong>
                {slide.subtitle && <p style={{ fontSize: '12px', color: '#666' }}>{slide.subtitle}</p>}
                {slide.bullets && slide.bullets.length > 0 && (
                  <ul style={{ marginTop: '5px' }}>
                    {slide.bullets.map((bullet, idx) => {
                      const bulletText = typeof bullet === 'string' ? bullet : bullet?.text || '';
                      return (
                        <li key={idx} style={{ fontSize: '12px' }}>
                          {bulletText}
                        </li>
                      );
                    })}
                  </ul>
                )}
              </div>
            ))}
          </div>
        </Card>

        <Card className="preview-actions">
          <div style={{ display: 'flex', gap: '10px', justifyContent: 'center' }}>
            <Button onClick={onEditPresentation} size="large">
              ← Edit & Regenerate
            </Button>
            <Button type="primary" onClick={onConfirmPresentation} size="large">
              View Full Presentation →
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="create-presentation-container">
      <Card className="create-form-card">
        <h1>🎨 Create New Presentation</h1>
        <p className="form-subtitle">
          Provide your content and let our AI create a professional presentation structure
        </p>

        <Form form={form} onFinish={onGeneratePresentation} layout="vertical">
          <Form.Item
            name="topic"
            label="Topic"
            rules={[{ required: true, message: 'Please enter the presentation topic' }]}
          >
            <Input className="form-input" placeholder="e.g., Machine Learning Basics, Product Launch, Sales Strategy" />
          </Form.Item>

          {/* Template Selection Card - Collapsible */}
          <Card 
            className="template-selection-card" 
            style={{ 
              marginBottom: '25px',
              borderLeft: `4px solid #2f6690`,
              backgroundColor: '#fafbfc',
              cursor: 'pointer'
            }}
            onClick={() => setShowTemplateSelector(!showTemplateSelector)}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <h3 style={{ marginTop: 0, color: '#2f6690', marginBottom: '5px' }}>
                  🎨 Select Your Template
                </h3>
                <p style={{ color: '#666', marginBottom: 0, fontSize: '14px' }}>
                  {showTemplateSelector ? 'Choose a professional template:' : 'Click to select template'}
                </p>
              </div>
              <span style={{ fontSize: '20px', transition: 'transform 0.3s ease', transform: showTemplateSelector ? 'rotate(180deg)' : 'rotate(0deg)' }}>
                ▼
              </span>
            </div>

            {/* Collapsible Template Selector */}
            {showTemplateSelector && (
              <div style={{ marginTop: '20px', paddingTop: '20px', borderTop: '1px solid #e0e0e0' }}>
                <p style={{ color: '#888', marginBottom: '15px', fontSize: '13px' }}>
                  Choose a professional template for your presentation. You can change this anytime.
                </p>
                <TemplateSelector value={selectedTemplate} onChange={setSelectedTemplate} />
              </div>
            )}
          </Card>

          <Form.Item
            name="presentation_title"
            label="Presentation Title (Optional)"
          >
            <Input className="form-input" placeholder="Leave empty to auto-generate title" />
          </Form.Item>

          <Form.Item
            name="raw_content"
            label="Raw Content"
            rules={[
              { required: true, message: 'Please provide content' },
              { min: 50, message: 'Content must be at least 50 characters' }
            ]}
          >
            <TextArea
              className="form-textarea"
              placeholder="Paste your content here. Include paragraphs, bullet points, or any unstructured text."
              rows={8}
            />
          </Form.Item>

          <Divider style={{ margin: '30px 0' }} />

          <Row gutter={16}>
            <Col xs={24} md={12}>
              <Form.Item
                name="target_audience"
                label="Target Audience"
                rules={[{ required: true, message: 'Please specify the audience' }]}
              >
                <Input className="form-input" placeholder="e.g., Business Executives, Students, Investors" />
              </Form.Item>
            </Col>

            <Col xs={24} md={12}>
              <Form.Item
                name="tone"
                label="Presentation Tone"
                rules={[{ required: true, message: 'Please select a tone' }]}
              >
                <Select placeholder="Select tone" className="form-select">
                  <Option value="professional">Professional</Option>
                  <Option value="casual">Casual</Option>
                  <Option value="academic">Academic</Option>
                  <Option value="persuasive">Persuasive</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col xs={24} md={12}>
              <Form.Item
                name="subject"
                label="Subject/Field (Optional)"
                initialValue="general"
              >
                <Select placeholder="Select subject" className="form-select">
                  <Option value="general">📚 General</Option>
                  <Option value="english">📖 English</Option>
                  <Option value="urdu">🇵🇰 اردو Urdu</Option>
                  <Option value="science">🔬 Science</Option>
                  <Option value="biology">🧬 Biology</Option>
                  <Option value="physics">⚛️ Physics</Option>
                  <Option value="medical">🏥 Medical</Option>
                  <Option value="it">💻 IT</Option>
                  <Option value="engineering">🔧 Engineering</Option>
                </Select>
              </Form.Item>
            </Col>

            <Col xs={24} md={12}>
              <Form.Item
                name="slide_ratio"
                label="Slide Format"
                initialValue="16:9"
              >
                <Select placeholder="Select slide format" className="form-select">
                  <Option value="16:9">🖥️ Widescreen (16:9)</Option>
                  <Option value="4:3">📺 Standard (4:3)</Option>
                  <Option value="1:1">□ Square (1:1)</Option>
                  <Option value="2:3">📱 Portrait (2:3)</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col xs={24} md={12}>
              <Form.Item
                name="num_slides"
                label="Number of Slides (Optional)"
              >
                <Input type="number" className="form-input" min="3" max="100" placeholder="e.g., 5, 7, 10, 50" />
              </Form.Item>
            </Col>

            <Col xs={24} md={12}>
              <Form.Item
                name="bullet_style"
                label="Bullet Point Style"
                initialValue="numbered"
              >
                <Select placeholder="Select bullet style" className="form-select">
                  <Option value="numbered">1️⃣ Numbered (1, 2, 3...)</Option>
                  <Option value="bullet_elegant">● Elegant Bullets</Option>
                  <Option value="bullet_modern">▸ Modern Bullets</Option>
                  <Option value="bullet_professional">■ Professional Bullets</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col xs={24} md={12}></Col>

            <Col xs={24} md={12}>
              <Form.Item
                name="enable_visuals"
                label="Professional Visuals"
                valuePropName="checked"
                initialValue={true}
              >
                <Checkbox>Add visual suggestions per bullet</Checkbox>
              </Form.Item>
            </Col>
          </Row>

          <Alert
            message="📋 Required Fields"
            description="Make sure you have filled in: Topic, Raw Content, Target Audience, and Presentation Tone"
            type="warning"
            showIcon
            style={{ marginBottom: '20px' }}
          />

          <Button 
            type="primary" 
            htmlType="submit" 
            loading={loading} 
            block 
            size="large"
            icon={<PlusOutlined />}
            className="generate-button"
          >
            Generate Presentation
          </Button>
        </Form>
      </Card>
    </div>
  );
}

export default CreatePresentation;
