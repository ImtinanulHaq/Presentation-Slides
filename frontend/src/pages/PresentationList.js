import React, { useEffect, useState } from 'react';
import { Card, Row, Col, Button, Empty, Spin } from 'antd';
import { Link } from 'react-router-dom';
import { presentationService } from '../services/api';

function PresentationList() {
  const [presentations, setPresentations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPresentations();
  }, []);

  const fetchPresentations = async () => {
    try {
      setLoading(true);
      const response = await presentationService.getAll();
      // Handle both paginated (results array) and direct array responses
      const data = response.data?.results || response.data || [];
      setPresentations(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Error fetching presentations:', error);
      setPresentations([]);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <Spin size="large" />;
  }

  return (
    <div>
      <h1>Presentations</h1>
      {presentations.length === 0 ? (
        <Empty description="No presentations found" />
      ) : (
        <Row gutter={[16, 16]}>
          {presentations.map((presentation) => (
            <Col xs={24} sm={12} md={8} key={presentation.id}>
              <Card
                title={presentation.title}
                extra={
                  <Link to={`/presentation/${presentation.id}`}>
                    <Button type="primary">View</Button>
                  </Link>
                }
              >
                <p>{presentation.description}</p>
                <p>Slides: {presentation.slides.length}</p>
              </Card>
            </Col>
          ))}
        </Row>
      )}
    </div>
  );
}

export default PresentationList;
