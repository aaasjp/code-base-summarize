import React, { useState, useEffect } from 'react';
import { Tree, Card, Typography, Spin, message, Row, Col, Button, Space, Empty } from 'antd';
import { FolderOutlined, FileOutlined, DownloadOutlined, ReloadOutlined, BookOutlined } from '@ant-design/icons';
import axios from 'axios';

const { Title, Text } = Typography;

const DocsExplorer = ({ fileId }) => {
  const [treeData, setTreeData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDoc, setSelectedDoc] = useState(null);
  const [docContent, setDocContent] = useState(null);
  const [contentLoading, setContentLoading] = useState(false);

  useEffect(() => {
    if (fileId) {
      loadDocsStructure();
    }
  }, [fileId]);

  const loadDocsStructure = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`/api/analysis/docs/${fileId}`);
      
      if (response.data.success) {
        const treeNodes = convertToTreeData(response.data.data.docs);
        setTreeData(treeNodes);
      } else {
        message.error('加载文档结构失败');
      }
    } catch (error) {
      console.error('加载文档结构错误:', error);
      message.error('加载文档结构失败');
    } finally {
      setLoading(false);
    }
  };

  const convertToTreeData = (docs) => {
    return docs.map(doc => {
      const children = doc.files.map(file => ({
        title: (
          <div className="file-item">
            <FileOutlined className="file-icon" style={{ color: '#52c41a' }} />
            <span className="file-name">{file.name}</span>
            <span className="file-size">
              {(file.size / 1024).toFixed(1)} KB
            </span>
          </div>
        ),
        key: `${doc.directory_name}/${file.name}`,
        isLeaf: true,
        data: {
          ...file,
          directory_name: doc.directory_name,
          full_path: `${doc.directory_name}/${file.name}`
        },
      }));

      return {
        title: (
          <div className="file-item">
            <FolderOutlined className="file-icon" style={{ color: '#1890ff' }} />
            <span className="file-name">{doc.directory_name}</span>
            <span className="file-count">
              {doc.files.length} 个文档
            </span>
          </div>
        ),
        key: doc.directory_name,
        children: children,
        isLeaf: false,
      };
    });
  };

  const handleDocSelect = async (selectedKeys, info) => {
    if (selectedKeys.length === 0) return;
    
    const key = selectedKeys[0];
    const node = info.node;
    
    if (node.isLeaf && node.data) {
      setSelectedDoc(node.data);
      await loadDocContent(key);
    }
  };

  const loadDocContent = async (docPath) => {
    try {
      setContentLoading(true);
      const [directoryName, filename] = docPath.split('/');
      
      const response = await axios.get(`/api/analysis/docs/${fileId}/${directoryName}/${filename}`, {
        responseType: 'text'
      });
      
      if (response.status === 200) {
        setDocContent(response.data);
      } else {
        message.error('读取文档内容失败');
      }
    } catch (error) {
      console.error('读取文档内容错误:', error);
      message.error('读取文档内容失败');
    } finally {
      setContentLoading(false);
    }
  };

  const handleDownloadDoc = async () => {
    if (!selectedDoc) return;
    
    try {
      const response = await axios.get(`/api/analysis/docs/${fileId}/${selectedDoc.directory_name}/${selectedDoc.name}`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', selectedDoc.name);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      message.success('文档下载成功');
    } catch (error) {
      console.error('下载文档错误:', error);
      message.error('文档下载失败');
    }
  };

  const renderDocContent = () => {
    if (!docContent) return null;

    // 如果是Markdown内容，简单渲染
    if (typeof docContent === 'string') {
      return (
        <div className="doc-preview">
          {docContent}
        </div>
      );
    }

    return (
      <div style={{ textAlign: 'center', padding: 40 }}>
        <FileOutlined style={{ fontSize: 48, color: '#d9d9d9' }} />
        <Text type="secondary" style={{ display: 'block', marginTop: 16 }}>
          无法预览此文档，请下载查看
        </Text>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="loading-container">
        <Spin size="large" />
        <Text style={{ marginLeft: 16 }}>正在加载文档结构...</Text>
      </div>
    );
  }

  return (
    <div>
      <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
        <Col>
          <Title level={2}>代码文档</Title>
          <Text type="secondary">
            查看生成的代码文档，支持按目录结构浏览
          </Text>
        </Col>
        <Col>
          <Button 
            icon={<ReloadOutlined />}
            onClick={loadDocsStructure}
            loading={loading}
          >
            刷新文档
          </Button>
        </Col>
      </Row>

      <Row gutter={16} style={{ marginTop: 24 }}>
        <Col span={8}>
          <Card title="文档结构" className="docs-tree">
            {treeData.length > 0 ? (
              <Tree
                treeData={treeData}
                onSelect={handleDocSelect}
                showLine
                showIcon={false}
                height={600}
                style={{ overflow: 'auto' }}
              />
            ) : (
              <Empty 
                description="暂无生成的文档"
                image={<BookOutlined style={{ fontSize: 48, color: '#d9d9d9' }} />}
              />
            )}
          </Card>
        </Col>
        
        <Col span={16}>
          {selectedDoc && (
            <Card 
              title={
                <Space>
                  <FileOutlined />
                  {selectedDoc.name}
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    {(selectedDoc.size / 1024).toFixed(1)} KB
                  </Text>
                </Space>
              }
              extra={
                <Space>
                  <Button 
                    icon={<ReloadOutlined />} 
                    size="small"
                    onClick={() => loadDocContent(selectedDoc.full_path)}
                  >
                    刷新
                  </Button>
                  <Button 
                    icon={<DownloadOutlined />} 
                    size="small"
                    onClick={handleDownloadDoc}
                  >
                    下载
                  </Button>
                </Space>
              }
              className="doc-content"
            >
              {contentLoading ? (
                <div className="loading-container">
                  <Spin />
                  <Text style={{ marginLeft: 16 }}>正在加载文档内容...</Text>
                </div>
              ) : (
                renderDocContent()
              )}
            </Card>
          )}
          
          {!selectedDoc && (
            <Card className="doc-content">
              <div style={{ textAlign: 'center', padding: 40 }}>
                <BookOutlined style={{ fontSize: 48, color: '#d9d9d9' }} />
                <Text type="secondary" style={{ display: 'block', marginTop: 16 }}>
                  请从左侧选择文档查看内容
                </Text>
              </div>
            </Card>
          )}
        </Col>
      </Row>
    </div>
  );
};

export default DocsExplorer; 