import React, { useState } from 'react';
import { Modal, Form, Input, Button, Space, Divider, Tag, Collapse, Spin, message, Empty, Card, Row, Col, InputNumber } from 'antd';
import { CopyOutlined, DownloadOutlined, CheckCircleOutlined } from '@ant-design/icons';

function ScriptGenerationModal({ visible, onCancel, presentation, onScriptGenerated }) {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [scripts, setScripts] = useState(null);
  const [metadata, setMetadata] = useState(null);

  const handleGenerateScript = async (values) => {
    try {
      setLoading(true);
      
      const token = process.env.REACT_APP_API_TOKEN || 'b1bf242b1c8a2b638e79f0b282599ffafea3faf3';
      const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
      
      const response = await fetch(
        `${apiUrl}/presentations/${presentation.id}/generate_script/`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Token ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            total_duration: values.total_duration,
          }),
        }
      );

      if (!response.ok) {
        throw new Error(`Failed to generate script: ${response.statusText}`);
      }

      const data = await response.json();
      
      if (data.success) {
        setScripts(data.scripts);
        setMetadata(data.metadata);
        message.success('✅ Scripts generated successfully!');
      } else {
        message.error(`❌ ${data.error}`);
      }
    } catch (error) {
      console.error('Error generating script:', error);
      message.error(`Failed to generate script: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    message.success('Copied to clipboard!');
  };

  const downloadScripts = () => {
    if (!scripts || !presentation) return;

    let content = `SPEAKER SCRIPTS FOR: ${presentation.title}\n`;
    content += `Presentation Tone: ${presentation.tone}\n`;
    content += `Total Duration: ${metadata.total_duration} minutes\n`;
    content += `Duration per Slide: ${metadata.duration_per_slide} minutes\n`;
    content += `${'='.repeat(80)}\n\n`;

    scripts.forEach((script, index) => {
      content += `SLIDE ${script.slide_number}: ${script.slide_title}\n`;
      content += `${'-'.repeat(60)}\n`;
      content += `📋 SLIDE EXPLANATION:\n${script.slide_explanation}\n\n`;
      content += `🎤 SPEAKER SCRIPT:\n${script.script}\n\n`;
      
      if (script.key_points && script.key_points.length > 0) {
        content += `📌 KEY POINTS:\n`;
        script.key_points.forEach(point => {
          content += `  • ${point}\n`;
        });
        content += '\n';
      }

      if (script.talking_points) {
        content += `💡 SPEAKING NOTES:\n${script.talking_points}\n\n`;
      }

      content += `⏱️ Estimated Duration: ${script.estimated_duration_seconds} seconds\n`;
      
      if (script.transition_to_next) {
        content += `➜ TRANSITION TO NEXT SLIDE:\n${script.transition_to_next}\n`;
      }

      content += `\n${'='.repeat(80)}\n\n`;
    });

    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${presentation.title}_scripts.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    message.success('Scripts downloaded successfully!');
  };

  const renderScriptContent = () => {
    if (!scripts || scripts.length === 0) {
      return <Empty description="No scripts generated yet" />;
    }

    // Calculate chunk boundaries for visual grouping
    const chunkSize = metadata.processing_mode === 'chunked' ? Math.ceil(scripts.length / metadata.num_chunks) : scripts.length;
    
    const scriptItems = scripts.map((script, index) => {
      const durationMinutes = (script.estimated_duration_seconds / 60).toFixed(1);
      // Use a combination of presentation ID and slide number to ensure uniqueness
      const uniqueKey = `${presentation.id}-${script.slide_number}-${index}`;
      
      // Determine which chunk this slide belongs to
      const chunkNumber = metadata.processing_mode === 'chunked' ? Math.floor(index / chunkSize) + 1 : 1;
      const isChunkStart = metadata.processing_mode === 'chunked' && index % chunkSize === 0;
      const isChunkEnd = metadata.processing_mode === 'chunked' && (index + 1) % chunkSize === 0;
      
      return {
        key: uniqueKey,
        label: (
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%' }}>
            <span>
              <strong>Slide {script.slide_number}</strong>: {script.slide_title}
              {metadata.processing_mode === 'chunked' && (
                <Tag color="orange" style={{ marginLeft: '8px', fontSize: '11px' }}>
                  Chunk {chunkNumber}
                </Tag>
              )}
            </span>
            <Tag color="blue" style={{ marginRight: 0 }}>
              ⏱️ {durationMinutes} min
            </Tag>
          </div>
        ),
        children: (
          <div style={{ maxHeight: '600px', overflowY: 'auto' }}>
            {/* Chunk Start Indicator */}
            {isChunkStart && metadata.processing_mode === 'chunked' && index > 0 && (
              <Card style={{ marginBottom: '16px', backgroundColor: '#f0f0f0', borderLeft: '4px solid #ff7a45' }}>
                <div style={{ color: '#ff7a45', fontWeight: 'bold', fontSize: '12px' }}>
                  ▶ Chunk {chunkNumber} Starts Here
                </div>
              </Card>
            )}
            {/* Slide Explanation */}
            <Card style={{ marginBottom: '16px', backgroundColor: '#f0f5ff' }}>
              <div style={{ marginBottom: '12px' }}>
                <Tag color="cyan" icon={<CheckCircleOutlined />}>Slide Explanation</Tag>
              </div>
              <p style={{ fontSize: '14px', lineHeight: '1.6', color: '#262626' }}>
                {script.slide_explanation}
              </p>
            </Card>

            {/* Speaker Script */}
            <Card style={{ marginBottom: '16px' }}>
              <div style={{ marginBottom: '12px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Tag color="green">Speaker Script</Tag>
                <Button 
                  type="text" 
                  size="small" 
                  icon={<CopyOutlined />}
                  onClick={() => copyToClipboard(script.script)}
                >
                  Copy
                </Button>
              </div>
              <div style={{ 
                backgroundColor: '#fafafa', 
                padding: '12px', 
                borderRadius: '4px',
                lineHeight: '1.8',
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-word',
                color: '#262626',
                fontSize: '14px'
              }}>
                {script.script}
              </div>
            </Card>

            {/* Key Points */}
            {script.key_points && script.key_points.length > 0 && (
              <Card style={{ marginBottom: '16px' }}>
                <div style={{ marginBottom: '12px' }}>
                  <Tag color="orange">Key Points</Tag>
                </div>
                <ul style={{ margin: 0, paddingLeft: '20px' }}>
                  {script.key_points.map((point, idx) => (
                    <li key={`${uniqueKey}-point-${idx}`} style={{ marginBottom: '8px', color: '#262626' }}>
                      {point}
                    </li>
                  ))}
                </ul>
              </Card>
            )}

            {/* Speaker Notes */}
            {script.talking_points && (
              <Card style={{ marginBottom: '16px' }}>
                <div style={{ marginBottom: '12px' }}>
                  <Tag color="purple">Speaking Notes</Tag>
                </div>
                <p style={{ margin: 0, color: '#262626', lineHeight: '1.6' }}>
                  {script.talking_points}
                </p>
              </Card>
            )}

            {/* Transition */}
            {script.transition_to_next && (
              <Card style={{ marginBottom: '16px', backgroundColor: '#f6ffed' }}>
                <div style={{ marginBottom: '12px' }}>
                  <Tag color="green">Transition to Next Slide</Tag>
                </div>
                <p style={{ margin: 0, color: '#262626', fontStyle: 'italic', lineHeight: '1.6' }}>
                  {script.transition_to_next}
                </p>
              </Card>
            )}

            {/* Timing Info */}
            <Card style={{ backgroundColor: '#fffbe6' }}>
              <Row gutter={16}>
                <Col span={12}>
                  <div style={{ fontSize: '12px', color: '#8c8c8c' }}>Duration</div>
                  <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#262626' }}>
                    {durationMinutes} min ({script.estimated_duration_seconds}s)
                  </div>
                </Col>
              </Row>
            </Card>
          </div>
        ),
      };
    });

    // Add chunk linking information when in chunked mode
    let chunkedItems = scriptItems;
    if (metadata.processing_mode === 'chunked') {
      // Group items by chunk and add chunk headers
      const itemsByChunk = [];
      const chunkSize = Math.ceil(scripts.length / metadata.num_chunks);
      
      for (let chunkIdx = 0; chunkIdx < metadata.num_chunks; chunkIdx++) {
        const chunkStart = chunkIdx * chunkSize;
        const chunkEnd = Math.min((chunkIdx + 1) * chunkSize, scripts.length);
        const chunkScripts = scriptItems.slice(chunkStart, chunkEnd);
        
        // Add chunk header
        const chunkHeaderKey = `chunk-${chunkIdx}`;
        const firstSlideNum = scripts[chunkStart].slide_number;
        const lastSlideNum = scripts[chunkEnd - 1].slide_number;
        
        itemsByChunk.push({
          key: chunkHeaderKey,
          label: (
            <div style={{ 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'space-between',
              width: '100%',
              backgroundColor: '#fff7e6',
              borderRadius: '4px',
              padding: '8px 12px',
              fontWeight: 'bold',
              color: '#ff7a45'
            }}>
              <span>📦 Chunk {chunkIdx + 1} of {metadata.num_chunks}</span>
              <span style={{ fontSize: '12px', fontWeight: 'normal' }}>Slides {firstSlideNum}-{lastSlideNum}</span>
            </div>
          ),
          children: (
            <div style={{ backgroundColor: '#fafafa', padding: '12px', borderRadius: '4px' }}>
              {chunkIdx > 0 && (
                <Card style={{ marginBottom: '16px', backgroundColor: '#f0f5ff', borderLeft: '4px solid #1890ff' }}>
                  <div style={{ color: '#1890ff', fontSize: '12px' }}>
                    ⬅️ <strong>Previous Chunk:</strong> Chunk {chunkIdx} (Slides {scripts[chunkStart - chunkSize].slide_number}-{scripts[Math.min(chunkStart - 1, scripts.length - 1)].slide_number})
                  </div>
                </Card>
              )}
              <Collapse items={chunkScripts} />
              {chunkIdx < metadata.num_chunks - 1 && (
                <Card style={{ marginTop: '16px', backgroundColor: '#f6ffed', borderLeft: '4px solid #52c41a' }}>
                  <div style={{ color: '#52c41a', fontSize: '12px' }}>
                    <strong>Next Chunk:</strong> Chunk {chunkIdx + 2} (Slides {scripts[chunkEnd].slide_number}-{scripts[Math.min(chunkEnd + chunkSize - 1, scripts.length - 1)].slide_number}) ➡️
                  </div>
                </Card>
              )}
            </div>
          ),
          disabled: false,
        });
      }
      chunkedItems = itemsByChunk;
    }

    return (
      <div>
        <div style={{ marginBottom: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <strong>Generated Scripts</strong>
            <span style={{ marginLeft: '12px', color: '#8c8c8c', fontSize: '12px' }}>
              {scripts.length} slides • Total: {metadata.total_duration} minutes
            </span>
            {metadata.processing_mode === 'chunked' && (
              <span style={{ marginLeft: '12px', color: '#1890ff', fontSize: '12px', fontWeight: 'bold' }}>
                📦 {metadata.num_chunks} chunks processed
              </span>
            )}
          </div>
          <Button 
            type="primary" 
            icon={<DownloadOutlined />}
            onClick={downloadScripts}
          >
            Download All Scripts
          </Button>
        </div>
        {metadata.processing_mode === 'chunked' ? (
          <Collapse items={chunkedItems} defaultActiveKey={['chunk-0']} />
        ) : (
          <Collapse items={scriptItems} defaultActiveKey={['1']} />
        )}
      </div>
    );
  };

  return (
    <Modal
      title="🎤 Generate Speaker Scripts"
      visible={visible}
      onCancel={onCancel}
      width={1000}
      footer={null}
      style={{ maxHeight: '90vh', overflowY: 'auto' }}
    >
      {!scripts ? (
        <div>
          <Divider>Configure Script Generation</Divider>
          
          <Card style={{ marginBottom: '24px', backgroundColor: '#f0f5ff' }}>
            <p style={{ marginBottom: '8px' }}>
              <strong>Presentation:</strong> {presentation.title}
            </p>
            <p style={{ marginBottom: '8px' }}>
              <strong>Tone:</strong> <Tag color="blue">{presentation.tone}</Tag>
            </p>
            <p style={{ marginBottom: 0 }}>
              <strong>Slides:</strong> {presentation.slides?.length || 0}
            </p>
          </Card>

          <Form
            form={form}
            layout="vertical"
            onFinish={handleGenerateScript}
          >
            <Form.Item
              label="Total Presentation Duration (minutes)"
              name="total_duration"
              rules={[
                { required: true, message: 'Please enter the presentation duration' },
                { 
                  pattern: /^[0-9]*\.?[0-9]+$/, 
                  message: 'Please enter a valid number' 
                },
                {
                  validator: (_, value) => {
                    if (value && parseFloat(value) > 0) {
                      return Promise.resolve();
                    }
                    return Promise.reject(new Error('Duration must be greater than 0'));
                  }
                }
              ]}
            >
              <InputNumber 
                min={0.5} 
                step={0.5}
                placeholder="e.g., 10, 15, 20" 
                style={{ width: '100%' }}
              />
            </Form.Item>

            <p style={{ fontSize: '12px', color: '#8c8c8c', marginTop: '-10px', marginBottom: '16px' }}>
              💡 Example: If you have 5 slides and want a 10-minute presentation, enter "10" 
              to distribute 2 minutes per slide.
            </p>

            <Divider />

            <Space style={{ width: '100%', justifyContent: 'flex-end' }}>
              <Button onClick={onCancel}>Cancel</Button>
              <Button 
                type="primary" 
                htmlType="submit"
                loading={loading}
                size="large"
              >
                {loading ? 'Generating Scripts...' : '🎬 Generate Scripts'}
              </Button>
            </Space>
          </Form>

          <Divider />

          <Card style={{ backgroundColor: '#f6ffed', borderColor: '#b7eb8f' }}>
            <h4>✨ What you'll get:</h4>
            <ul style={{ marginBottom: 0 }}>
              <li>Professional speaker scripts for each slide</li>
              <li>Paragraph-wise breakdown for natural delivery</li>
              <li>Key points and talking notes</li>
              <li>Smooth transitions between slides</li>
              <li>Precise timing for each slide</li>
              <li>Slide explanations and context</li>
            </ul>
          </Card>
        </div>
      ) : (
        <div>
          {loading ? (
            <div style={{ textAlign: 'center', padding: '40px' }}>
              <Spin size="large" tip="Generating scripts..." />
            </div>
          ) : (
            <>
              <Divider>Scripts Ready</Divider>
              {renderScriptContent()}
              
              <div style={{ marginTop: '24px', display: 'flex', gap: '8px' }}>
                <Button onClick={() => setScripts(null)}>
                  Generate New Script
                </Button>
                <Button type="primary" onClick={onCancel}>
                  Close
                </Button>
              </div>
            </>
          )}
        </div>
      )}
    </Modal>
  );
}

export default ScriptGenerationModal;
