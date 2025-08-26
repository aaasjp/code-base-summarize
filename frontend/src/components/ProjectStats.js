import React, { useState, useEffect } from 'react';
import { Card, Typography, Spin, message, Row, Col, Progress, List, Tag } from 'antd';
import { BarChartOutlined, FileOutlined, FolderOutlined, HddOutlined } from '@ant-design/icons';
import axios from 'axios';

const { Title, Text } = Typography;

const ProjectStats = ({ fileId }) => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (fileId) {
      loadProjectStats();
    }
  }, [fileId]);

  const loadProjectStats = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`/api/analysis/stats/${fileId}`);
      
      if (response.data.success) {
        setStats(response.data.data.stats);
      } else {
        message.error('加载项目统计失败');
      }
    } catch (error) {
      console.error('加载项目统计错误:', error);
      message.error('加载项目统计失败');
    } finally {
      setLoading(false);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const getExtensionColor = (extension) => {
    const colors = {
      '.js': 'blue',
      '.ts': 'cyan',
      '.jsx': 'geekblue',
      '.tsx': 'purple',
      '.py': 'green',
      '.java': 'orange',
      '.cpp': 'red',
      '.c': 'volcano',
      '.cs': 'magenta',
      '.php': 'lime',
      '.html': 'gold',
      '.css': 'pink',
      '.json': 'default',
      '.xml': 'processing',
      '.md': 'success',
      '.txt': 'warning'
    };
    return colors[extension] || 'default';
  };

  if (!fileId) {
    return (
      <div style={{ textAlign: 'center', padding: 60 }}>
        <BarChartOutlined style={{ fontSize: 64, color: '#d9d9d9', marginBottom: 24 }} />
        <Title level={3} type="secondary">请选择项目</Title>
        <Text type="secondary" style={{ display: 'block', marginTop: 16 }}>
          请从顶部选择器中选择一个项目来查看项目统计信息
        </Text>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="loading-container">
        <Spin size="large" />
        <Text style={{ marginLeft: 16 }}>正在加载项目统计...</Text>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="error-message">
        <Text>无法加载项目统计信息</Text>
      </div>
    );
  }

  const totalItems = stats.total_files + stats.total_directories;
  const filePercentage = totalItems > 0 ? (stats.total_files / totalItems) * 100 : 0;
  const dirPercentage = totalItems > 0 ? (stats.total_directories / totalItems) * 100 : 0;

  return (
    <div>
      <Title level={2}>项目统计</Title>
      <Text type="secondary">
        项目文件结构和统计信息概览
      </Text>

      {/* 基础统计 */}
      <Row gutter={16} style={{ marginTop: 24 }}>
        <Col span={6}>
          <Card className="stats-item">
            <FileOutlined style={{ fontSize: 32, color: '#1890ff', marginBottom: 16 }} />
            <div className="stats-number">{stats.total_files}</div>
            <div className="stats-label">代码文件</div>
          </Card>
        </Col>
        <Col span={6}>
          <Card className="stats-item">
            <FolderOutlined style={{ fontSize: 32, color: '#52c41a', marginBottom: 16 }} />
            <div className="stats-number">{stats.total_directories}</div>
            <div className="stats-label">目录</div>
          </Card>
        </Col>
        <Col span={6}>
          <Card className="stats-item">
            <HddOutlined style={{ fontSize: 32, color: '#faad14', marginBottom: 16 }} />
            <div className="stats-number">{formatFileSize(stats.total_size)}</div>
            <div className="stats-label">总大小</div>
          </Card>
        </Col>
        <Col span={6}>
          <Card className="stats-item">
            <BarChartOutlined style={{ fontSize: 32, color: '#722ed1', marginBottom: 16 }} />
            <div className="stats-number">{stats.extensions.length}</div>
            <div className="stats-label">文件类型</div>
          </Card>
        </Col>
      </Row>

      {/* 文件类型分布 */}
      <Card title="文件类型分布" style={{ marginTop: 24 }}>
        <Row gutter={16}>
          <Col span={12}>
            <div style={{ marginBottom: 16 }}>
              <Text strong>文件与目录比例:</Text>
            </div>
            <div style={{ marginBottom: 8 }}>
              <Text>文件: {stats.total_files} ({filePercentage.toFixed(1)}%)</Text>
              <Progress 
                percent={filePercentage} 
                size="small" 
                strokeColor="#1890ff"
                style={{ marginTop: 4 }}
              />
            </div>
            <div>
              <Text>目录: {stats.total_directories} ({dirPercentage.toFixed(1)}%)</Text>
              <Progress 
                percent={dirPercentage} 
                size="small" 
                strokeColor="#52c41a"
                style={{ marginTop: 4 }}
              />
            </div>
          </Col>
          <Col span={12}>
            <div style={{ marginBottom: 16 }}>
              <Text strong>文件类型统计:</Text>
            </div>
            <div style={{ maxHeight: 200, overflowY: 'auto' }}>
              {stats.extensions.slice(0, 10).map((ext, index) => (
                <div key={ext.extension} style={{ marginBottom: 8 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Tag color={getExtensionColor(ext.extension)}>
                      {ext.extension}
                    </Tag>
                    <Text>{ext.count} 个文件</Text>
                  </div>
                  <Progress 
                    percent={(ext.count / stats.total_files) * 100} 
                    size="small" 
                    showInfo={false}
                    strokeColor={getExtensionColor(ext.extension)}
                  />
                </div>
              ))}
            </div>
          </Col>
        </Row>
      </Card>

      {/* 最大文件列表 */}
      <Card title="最大文件 (前10个)" style={{ marginTop: 24 }}>
        <List
          dataSource={stats.largest_files}
          renderItem={(file, index) => (
            <List.Item>
              <List.Item.Meta
                avatar={
                  <div style={{ 
                    width: 32, 
                    height: 32, 
                    borderRadius: '50%', 
                    backgroundColor: getExtensionColor(file.extension),
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'white',
                    fontSize: 12,
                    fontWeight: 'bold'
                  }}>
                    {file.extension.replace('.', '')}
                  </div>
                }
                title={
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <Text strong>{file.name}</Text>
                    <Tag color={getExtensionColor(file.extension)}>
                      {file.extension}
                    </Tag>
                  </div>
                }
                description={
                  <div>
                    <Text type="secondary">路径: {file.path}</Text>
                    <br />
                    <Text type="secondary">大小: {formatFileSize(file.size)}</Text>
                  </div>
                }
              />
              <div style={{ textAlign: 'right' }}>
                <Text type="secondary">#{index + 1}</Text>
              </div>
            </List.Item>
          )}
        />
      </Card>

      {/* 详细统计表格 */}
      <Card title="详细统计" style={{ marginTop: 24 }}>
        <Row gutter={16}>
          <Col span={12}>
            <Text strong>文件类型详细统计:</Text>
            <List
              size="small"
              style={{ marginTop: 8 }}
              dataSource={stats.extensions}
              renderItem={(ext) => (
                <List.Item>
                  <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%' }}>
                    <Tag color={getExtensionColor(ext.extension)}>
                      {ext.extension}
                    </Tag>
                    <Text>{ext.count} 个文件</Text>
                  </div>
                </List.Item>
              )}
            />
          </Col>
          <Col span={12}>
            <div>
              <Text strong>项目概览:</Text>
              <div style={{ marginTop: 8 }}>
                <p>• 总文件数: {stats.total_files}</p>
                <p>• 总目录数: {stats.total_directories}</p>
                <p>• 总大小: {formatFileSize(stats.total_size)}</p>
                <p>• 文件类型数: {stats.extensions.length}</p>
                <p>• 平均文件大小: {formatFileSize(stats.total_size / stats.total_files)}</p>
              </div>
            </div>
          </Col>
        </Row>
      </Card>
    </div>
  );
};

export default ProjectStats; 