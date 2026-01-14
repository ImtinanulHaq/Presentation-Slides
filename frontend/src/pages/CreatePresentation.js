import React, { useState } from 'react';
import { Form, Input, Button, Card, message, Select, Spin, Alert, Divider, Row, Col, Checkbox } from 'antd';
import { useNavigate } from 'react-router-dom';
import { PlusOutlined } from '@ant-design/icons';
import { presentationService } from '../services/api';

const { TextArea } = Input;
const { Option } = Select;

function CreatePresentation() {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState(1); // Step 1: Input, Step 2: Preview
  const [generatedPresentation, setGeneratedPresentation] = useState(null);
  const navigate = useNavigate();

  const onGeneratePresentation = async (values) => {
    try {
      setLoading(true);
      
      // Log ALL form values first to see what we're getting
      console.log('[FORM DATA RECEIVED] Complete values object:', values);
      console.log('[FORM DATA] Keys present:', Object.keys(values));
      console.log('[FORM DATA] Topic:', values.topic, '| Type:', typeof values.topic);
      console.log('[FORM DATA] Target Audience:', values.target_audience, '| Type:', typeof values.target_audience);
      console.log('[FORM DATA] Tone:', values.tone, '| Type:', typeof values.tone);
      console.log('[FORM DATA] Raw Content length:', values.raw_content?.length, '| Type:', typeof values.raw_content);
      
      // Validate critical required fields BEFORE sending to backend
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
          console.warn(`[❌ VALIDATION WARNING] Missing required field: ${label} (${field}) - Value is:`, values[field]);
        }
      }
      
      if (missingFields.length > 0) {
        console.error('[FORM VALIDATION FAILED]', missingFields);
        message.error(`❌ Missing required fields: ${missingFields.join(', ')}`);
        setLoading(false);
        return;
      }
      
      // Clean up form values - only send required and optional fields
      const cleanValues = {
        topic: values.topic?.trim(),
        raw_content: values.raw_content?.trim(),
        target_audience: values.target_audience?.trim(),
        tone: values.tone,
        presentation_title: values.presentation_title?.trim() || '',
        num_slides: values.num_slides ? parseInt(values.num_slides) : null,
        enable_chunking: values.enable_chunking === true,
        enable_visuals: values.enable_visuals === true
      };
      
      console.log('[✅ READY TO SUBMIT] All required fields present:');
      console.log('[DEBUG] Topic:', cleanValues.topic);
      console.log('[DEBUG] Target Audience:', cleanValues.target_audience);
      console.log('[DEBUG] Tone:', cleanValues.tone);
      console.log('[DEBUG] Content length:', cleanValues.raw_content?.length);
      console.log('[DEBUG] Num Slides:', cleanValues.num_slides);
      console.log('[DEBUG] Enable Visuals:', cleanValues.enable_visuals);
      console.log('[📤 SENDING TO BACKEND]', JSON.stringify(cleanValues, null, 2));
      
      // Call backend to generate presentation
      const response = await presentationService.generate(cleanValues);
      
      message.success('Presentation generated successfully!');
      setGeneratedPresentation(response.data);
      setStep(2);
    } catch (error) {
      console.error('[ERROR] Full error object:', error);
      console.error('[ERROR] Error response data:', error.response?.data);
      
      let errorMessage = 'Error generating presentation';
      
      // Handle different error scenarios professionally
      if (error.response?.status === 401) {
        errorMessage = 'Authentication failed: Invalid or expired token. Please refresh the page.';
      } else if (error.response?.status === 403) {
        errorMessage = 'Permission denied: You do not have access to this resource.';
      } else if (error.response?.status === 400) {
        // Extract detailed error from response
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
          console.error('[VALIDATION DETAILS]', errors);
        } else {
          errorMessage = `Bad request: ${backendError?.detail || 'Invalid input data'}`;
        }
      } else if (error.response?.status === 500) {
        errorMessage = 'Server error: The presentation generation failed. Please check the backend logs.';
      } else if (error.code === 'ERR_NETWORK' || error.message === 'Network Error') {
        errorMessage = 'Network error: Cannot connect to backend at http://localhost:8000/api. Make sure Django is running.';
      } else if (error.message?.includes('Receiving end does not exist')) {
        errorMessage = 'Backend not reachable. Make sure the Django server is running on port 8000.';
      }
      
      message.error(errorMessage);
      console.error('[ERROR] Complete error:', JSON.stringify(error, null, 2));
    } finally {
      setLoading(false);
    }
  };

  const onConfirmPresentation = async () => {
    try {
      // Save presentation (already saved in backend)
      message.success('Presentation saved!');
      navigate(`/presentation/${generatedPresentation.id}`);
    } catch (error) {
      message.error('Error saving presentation');
      console.error(error);
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
      <div>
        <Card style={{ marginBottom: '20px' }}>
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
            <Card title="Presentation Details" style={{ marginBottom: '20px' }}>
              <p><strong>Title:</strong> {generatedPresentation.title}</p>
              <p><strong>Topic:</strong> {generatedPresentation.topic}</p>
              <p><strong>Audience:</strong> {generatedPresentation.target_audience}</p>
              <p><strong>Tone:</strong> {generatedPresentation.tone}</p>
              <p><strong>Total Slides:</strong> {generatedPresentation.total_slides}</p>
            </Card>
          </Col>

          <Col xs={24} md={12}>
            <Card title="Content Summary">
              <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
                <p><strong>Raw Content:</strong></p>
                <p>{generatedPresentation.raw_content.substring(0, 200)}...</p>
              </div>
            </Card>
          </Col>
        </Row>

        <Card title="Generated Slides" style={{ marginTop: '20px', marginBottom: '20px' }}>
          <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
            {generatedPresentation.slides && generatedPresentation.slides.map((slide) => (
              <div key={slide.id} style={{ marginBottom: '15px', paddingBottom: '15px', borderBottom: '1px solid #f0f0f0' }}>
                <strong>Slide {slide.slide_number}: {slide.title}</strong>
                {slide.subtitle && <p style={{ fontSize: '12px', color: '#666' }}>{slide.subtitle}</p>}
                {slide.bullets && slide.bullets.length > 0 && (
                  <ul style={{ marginTop: '5px' }}>
                    {slide.bullets.map((bullet, idx) => {
                      // Handle both string and object bullets
                      const bulletText = typeof bullet === 'string' ? bullet : bullet?.text || '';
                      const bulletObj = typeof bullet === 'object' && bullet !== null ? bullet : null;
                      
                      return (
                        <li key={idx} style={{ fontSize: '12px' }}>
                          <span>
                            {bulletObj?.emoji && <span style={{ marginRight: '4px' }}>{bulletObj.emoji}</span>}
                            {bulletText}
                          </span>
                          {bulletObj && (bulletObj.icon || bulletObj.color) && (
                            <span style={{ marginLeft: '8px', fontSize: '10px', color: '#999' }}>
                              {bulletObj.icon && `[${bulletObj.icon}]`}
                              {bulletObj.color && ` <${bulletObj.color}>`}
                            </span>
                          )}
                        </li>
                      );
                    })}
                  </ul>
                )}
              </div>
            ))}
          </div>
        </Card>

        <Card style={{ marginTop: '20px' }}>
          <div style={{ display: 'flex', gap: '10px', justifyContent: 'center' }}>
            <Button onClick={onEditPresentation}>
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
    <Card style={{ maxWidth: '800px', margin: '0 auto' }}>
      <h1>🎨 Create New Presentation</h1>
      <p style={{ color: '#666', marginBottom: '20px' }}>
        Provide your content and let our AI create a professional presentation structure
      </p>

      <Form form={form} onFinish={onGeneratePresentation} layout="vertical">
        <Form.Item
          name="topic"
          label="Topic"
          rules={[{ required: true, message: 'Please enter the presentation topic' }]}
        >
          <Input placeholder="e.g., Machine Learning Basics, Product Launch, Sales Strategy" />
        </Form.Item>

        <Form.Item
          name="presentation_title"
          label="Presentation Title (Optional)"
        >
          <Input placeholder="Leave empty to auto-generate title" />
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
            placeholder="Paste your content here. Include paragraphs, bullet points, or any unstructured text. The AI will organize it into professional slides."
            rows={8}
          />
        </Form.Item>

        <Divider />

        <Row gutter={16}>
          <Col xs={24} md={12}>
            <Form.Item
              name="target_audience"
              label="Target Audience"
              rules={[{ required: true, message: 'Please specify the audience' }]}
            >
              <Input placeholder="e.g., Business Executives, Students, Investors" />
            </Form.Item>
          </Col>

          <Col xs={24} md={12}>
            <Form.Item
              name="tone"
              label="Presentation Tone"
              rules={[{ required: true, message: 'Please select a tone' }]}
            >
              <Select placeholder="Select tone">
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
              name="num_slides"
              label="Number of Slides (Optional)"
              tooltip="Leave empty for AI to decide (5-8 slides). Enter a number to specify exact count (3-100)."
            >
              <Input type="number" min="3" max="100" placeholder="e.g., 5, 7, 10, 50 (optional)" />
            </Form.Item>
          </Col>

          <Col xs={24} md={12}>
            <Form.Item
              name="enable_visuals"
              label="Professional Visuals"
              valuePropName="checked"
              tooltip="Add visual suggestions for each bullet point. LLM analyzes content and suggests icons, emojis, and colors."
            >
              <Checkbox>Add professional visual suggestions per bullet</Checkbox>
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col xs={24} md={24}>
            <Form.Item
              name="enable_chunking"
              label="Enable for Large Content"
              valuePropName="checked"
              tooltip="Automatically divide very large content into chunks for better processing. Useful when you have 5000+ words."
            >
              <Checkbox>Process large content in chunks</Checkbox>
            </Form.Item>
          </Col>
        </Row>

        <Alert
          message="📋 Required Fields"
          description="Make sure you have filled in:
          ✓ Topic (presentation subject)
          ✓ Raw Content (your content to structure)
          ✓ Target Audience (who will see this)
          ✓ Presentation Tone (professional, casual, academic, or persuasive)"
          type="warning"
          showIcon
          style={{ marginBottom: '20px' }}
        />

        <Alert
          message="AI-Powered Generation"
          description="Our system will analyze your content and automatically create:
          ✓ Up to 100 slides (specify count or let AI decide)
          ✓ Intelligent chunking for large content (5000+ words)
          ✓ Logical slide organization with clear sections
          ✓ Refined bullet points (max 12 words each)
          ✓ Relevant visual suggestions (icons, symbols, images)
          ✓ Professional speaker notes"
          type="info"
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
        >
          Generate Presentation
        </Button>
      </Form>
    </Card>
  );
}

export default CreatePresentation;
