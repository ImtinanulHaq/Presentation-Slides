import React from 'react';
import { Button, Card, Row, Col, Statistic, Tag, Space, Divider } from 'antd';
import { Link } from 'react-router-dom';
import { 
  RobotOutlined, 
  FileTextOutlined, 
  BgColorsOutlined,
  ThunderboltOutlined,
  TeamOutlined,
  CloudUploadOutlined,
  PlusOutlined,
  CheckCircleOutlined
} from '@ant-design/icons';
import '../styles/Home.css';

function Home() {
  return (
    <div className="home-container">
      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-content">
          <h1 className="hero-title">
            ✨ Transform Your Ideas Into Professional Presentations
          </h1>
          <p className="hero-subtitle">
            AI-powered presentation generator that creates stunning slides in seconds
          </p>
          <Space size="large" style={{ marginTop: '30px' }}>
            <Link to="/create">
              <Button 
                type="primary" 
                size="large" 
                icon={<PlusOutlined />}
                className="cta-button"
              >
                Create Presentation
              </Button>
            </Link>
            <Link to="/">
              <Button 
                size="large" 
                className="secondary-button"
              >
                View Dashboard
              </Button>
            </Link>
          </Space>
        </div>
      </section>

      {/* Features Section */}
      <section className="features-section">
        <div className="section-container">
          <h2 className="section-title">Powerful Features</h2>
          <p className="section-subtitle">Everything you need to create professional presentations</p>
          
          <Row gutter={[32, 32]} style={{ marginTop: '40px' }}>
            {/* Feature 1 */}
            <Col xs={24} sm={12} lg={8}>
              <Card className="feature-card" bordered={false}>
                <div className="feature-icon">
                  <RobotOutlined />
                </div>
                <h3 className="feature-title">AI-Powered Generation</h3>
                <p className="feature-description">
                  Leverage advanced AI to automatically generate slide content from your topics. Get perfectly structured presentations in seconds.
                </p>
              </Card>
            </Col>

            {/* Feature 2 */}
            <Col xs={24} sm={12} lg={8}>
              <Card className="feature-card" bordered={false}>
                <div className="feature-icon" style={{ color: '#81c3d7' }}>
                  <BgColorsOutlined />
                </div>
                <h3 className="feature-title">Professional Templates</h3>
                <p className="feature-description">
                  Choose from curated templates with premium color schemes. Warm Blue, Rose Elegance, and Warm Spectrum designs included.
                </p>
              </Card>
            </Col>

            {/* Feature 3 */}
            <Col xs={24} sm={12} lg={8}>
              <Card className="feature-card" bordered={false}>
                <div className="feature-icon" style={{ color: '#ee9b00' }}>
                  <FileTextOutlined />
                </div>
                <h3 className="feature-title">Smart Content Chunking</h3>
                <p className="feature-description">
                  Automatically divides content into optimal slide chunks. Perfect bullet points with 4-6 items per slide for maximum impact.
                </p>
              </Card>
            </Col>

            {/* Feature 4 */}
            <Col xs={24} sm={12} lg={8}>
              <Card className="feature-card" bordered={false}>
                <div className="feature-icon" style={{ color: '#f4acb7' }}>
                  <ThunderboltOutlined />
                </div>
                <h3 className="feature-title">Multiple Aspect Ratios</h3>
                <p className="feature-description">
                  Create presentations in any format: 16:9, 4:3, 1:1, or 2:3. Adapt to any screen size and presentation platform.
                </p>
              </Card>
            </Col>

            {/* Feature 5 */}
            <Col xs={24} sm={12} lg={8}>
              <Card className="feature-card" bordered={false}>
                <div className="feature-icon" style={{ color: '#94d2bd' }}>
                  <CloudUploadOutlined />
                </div>
                <h3 className="feature-title">One-Click Export</h3>
                <p className="feature-description">
                  Download presentation as PPTX file instantly. Ready to edit and present on any device. Professional quality guaranteed.
                </p>
              </Card>
            </Col>

            {/* Feature 6 */}
            <Col xs={24} sm={12} lg={8}>
              <Card className="feature-card" bordered={false}>
                <div className="feature-icon" style={{ color: '#d9dcd6' }}>
                  <TeamOutlined />
                </div>
                <h3 className="feature-title">Customizable & Editable</h3>
                <p className="feature-description">
                  Full control over every aspect. Edit content, adjust layouts, and fine-tune designs before exporting your final presentation.
                </p>
              </Card>
            </Col>
          </Row>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="how-it-works-section">
        <div className="section-container">
          <h2 className="section-title">How It Works</h2>
          <p className="section-subtitle">Create stunning presentations in 3 simple steps</p>
          
          <Row gutter={[32, 32]} style={{ marginTop: '40px' }}>
            <Col xs={24} sm={8}>
              <div className="step-card">
                <div className="step-number">1</div>
                <h3>Enter Your Content</h3>
                <p>Paste your topic, content, and key points. Specify your target audience and desired tone.</p>
              </div>
            </Col>
            <Col xs={24} sm={8}>
              <div className="step-card">
                <div className="step-number">2</div>
                <h3>AI Generates Slides</h3>
                <p>Our AI analyzes your content and automatically creates well-structured, professional slides.</p>
              </div>
            </Col>
            <Col xs={24} sm={8}>
              <div className="step-card">
                <div className="step-number">3</div>
                <h3>Download & Present</h3>
                <p>Review, edit if needed, and download as PPTX. Your presentation is ready to present!</p>
              </div>
            </Col>
          </Row>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="benefits-section">
        <div className="section-container">
          <Row gutter={[40, 40]} align="middle">
            <Col xs={24} lg={12}>
              <h2 className="section-title">Why Choose Us?</h2>
              <div style={{ marginTop: '30px' }}>
                {[
                  'Lightning-fast presentation creation',
                  'Professional quality templates',
                  'AI-powered content generation',
                  'Multiple export formats',
                  'Fully customizable designs',
                  'No subscription required'
                ].map((benefit, index) => (
                  <div key={index} className="benefit-item">
                    <CheckCircleOutlined className="benefit-icon" />
                    <span>{benefit}</span>
                  </div>
                ))}
              </div>
            </Col>
            <Col xs={24} lg={12}>
              <Card className="benefit-card" bordered={false}>
                <div className="benefit-stats">
                  <Statistic 
                    title="Presentations Created" 
                    value="1000+" 
                    valueStyle={{ color: '#2f6690' }}
                  />
                  <Divider />
                  <Statistic 
                    title="Time Saved" 
                    value="500+" 
                    suffix="hours"
                    valueStyle={{ color: '#81c3d7' }}
                  />
                  <Divider />
                  <Statistic 
                    title="Average Creation Time" 
                    value="2" 
                    suffix="minutes"
                    valueStyle={{ color: '#005f73' }}
                  />
                </div>
              </Card>
            </Col>
          </Row>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <div className="section-container">
          <h2 className="cta-title">Ready to Create Your First Presentation?</h2>
          <p className="cta-subtitle">Join thousands of professionals creating presentations faster</p>
          <Link to="/create">
            <Button 
              type="primary" 
              size="large" 
              icon={<PlusOutlined />}
              className="cta-button-large"
            >
              Start Creating Now
            </Button>
          </Link>
        </div>
      </section>
    </div>
  );
}

export default Home;
