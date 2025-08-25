import React, { useState, useEffect } from 'react';
import { Tree, Card, Typography, Spin, message, Row, Col, Button, Space } from 'antd';
import { FolderOutlined, FileOutlined, EyeOutlined, DownloadOutlined, BookOutlined } from '@ant-design/icons';
import axios from 'axios';
import FileViewer from './FileViewer';

const { Title, Text } = Typography;

const FileExplorer = ({ fileId, onShowDocs }) => {
  const [treeData, setTreeData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileContent, setFileContent] = useState(null);
  const [contentLoading, setContentLoading] = useState(false);
  const [generatingDocs, setGeneratingDocs] = useState(false);

  useEffect(() => {
    if (fileId) {
      loadProjectStructure();
    }
  }, [fileId]);

  const loadProjectStructure = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`/api/analysis/structure/${fileId}`);
      
      if (response.data.success) {
        const treeNodes = convertToTreeData(response.data.data.structure);
        setTreeData(treeNodes);
      } else {
        message.error('加载项目结构失败');
      }
    } catch (error) {
      console.error('加载项目结构错误:', error);
      message.error('加载项目结构失败');
    } finally {
      setLoading(false);
    }
  };

  const convertToTreeData = (structure) => {
    return structure.map(item => {
      if (item.type === 'directory') {
        return {
          title: (
            <div className="file-item">
              <FolderOutlined className="file-icon" style={{ color: '#1890ff' }} />
              <span className="file-name">{item.name}</span>
            </div>
          ),
          key: item.path,
          children: item.children ? convertToTreeData(item.children) : [],
          isLeaf: false,
        };
      } else {
        return {
          title: (
            <div className="file-item">
              <FileOutlined className="file-icon" style={{ color: '#52c41a' }} />
              <span className="file-name">{item.name}</span>
              <span className="file-size">
                {(item.size / 1024).toFixed(1)} KB
              </span>
            </div>
          ),
          key: item.path,
          isLeaf: true,
          data: item,
        };
      }
    });
  };

  const handleFileSelect = async (selectedKeys, info) => {
    if (selectedKeys.length === 0) return;
    
    const key = selectedKeys[0];
    const node = info.node;
    
    if (node.isLeaf && node.data) {
      setSelectedFile(node.data);
      await loadFileContent(key);
    }
  };

  const loadFileContent = async (filePath) => {
    try {
      setContentLoading(true);
      const response = await axios.get(`/api/analysis/file/${fileId}`, {
        params: { filePath }
      });
      
      if (response.data.success) {
        setFileContent(response.data.data);
      } else {
        message.error('读取文件内容失败');
      }
    } catch (error) {
      console.error('读取文件内容错误:', error);
      message.error('读取文件内容失败');
    } finally {
      setContentLoading(false);
    }
  };

  const handleDownloadFile = async () => {
    if (!selectedFile) return;
    
    try {
      const response = await axios.get(`/api/analysis/file/${fileId}`, {
        params: { filePath: selectedFile.path },
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', selectedFile.name);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      message.success('文件下载成功');
    } catch (error) {
      console.error('下载文件错误:', error);
      message.error('文件下载失败');
    }
  };

  const handleGenerateDocs = async () => {
    try {
      setGeneratingDocs(true);
      message.loading('正在生成代码文档，请稍候...', 0);
      
      const response = await axios.post(`/api/analysis/generate-docs/${fileId}`, {}, {
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      message.destroy();
      
      if (response.data.success) {
        const { success_count, error_count, total_directories } = response.data.data;
        message.success(`文档生成完成！成功处理 ${success_count} 个目录，失败 ${error_count} 个`);
        
        // 通知父组件显示文档
        if (onShowDocs) {
          onShowDocs();
        }
      } else {
        message.error('生成文档失败');
      }
    } catch (error) {
      message.destroy();
      console.error('生成文档错误:', error);
      message.error('生成文档失败: ' + (error.response?.data?.error || error.message));
    } finally {
      setGeneratingDocs(false);
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <Spin size="large" />
        <Text style={{ marginLeft: 16 }}>正在加载项目结构...</Text>
      </div>
    );
  }

  return (
    <div>
      <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
        <Col>
          <Title level={2}>文件浏览器</Title>
          <Text type="secondary">
            点击文件查看内容，支持代码高亮显示
          </Text>
        </Col>
        <Col>
          <Button 
            type="primary" 
            icon={<BookOutlined />}
            loading={generatingDocs}
            onClick={handleGenerateDocs}
            size="large"
          >
            生成代码文档
          </Button>
        </Col>
      </Row>

      <Row gutter={16} style={{ marginTop: 24 }}>
        <Col span={8}>
          <Card title="项目结构" className="file-tree">
            <Tree
              treeData={treeData}
              onSelect={handleFileSelect}
              showLine
              showIcon={false}
              height={600}
              style={{ overflow: 'auto' }}
            />
          </Card>
        </Col>
        
        <Col span={16}>
          {selectedFile && (
            <Card 
              title={
                <Space>
                  <FileOutlined />
                  {selectedFile.name}
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    {(selectedFile.size / 1024).toFixed(1)} KB
                  </Text>
                </Space>
              }
              extra={
                <Space>
                  <Button 
                    icon={<EyeOutlined />} 
                    size="small"
                    onClick={() => loadFileContent(selectedFile.path)}
                  >
                    刷新
                  </Button>
                  <Button 
                    icon={<DownloadOutlined />} 
                    size="small"
                    onClick={handleDownloadFile}
                  >
                    下载
                  </Button>
                </Space>
              }
              className="file-content"
            >
              {contentLoading ? (
                <div className="loading-container">
                  <Spin />
                  <Text style={{ marginLeft: 16 }}>正在加载文件内容...</Text>
                </div>
              ) : fileContent ? (
                <FileViewer 
                  content={fileContent.content}
                  fileName={fileContent.file_name}
                  extension={fileContent.extension}
                  lines={fileContent.lines}
                />
              ) : (
                <div style={{ textAlign: 'center', padding: 40 }}>
                  <FileOutlined style={{ fontSize: 48, color: '#d9d9d9' }} />
                  <Text type="secondary" style={{ display: 'block', marginTop: 16 }}>
                    点击文件查看内容
                  </Text>
                </div>
              )}
            </Card>
          )}
          
          {!selectedFile && (
            <Card className="file-content">
              <div style={{ textAlign: 'center', padding: 40 }}>
                <FileOutlined style={{ fontSize: 48, color: '#d9d9d9' }} />
                <Text type="secondary" style={{ display: 'block', marginTop: 16 }}>
                  请从左侧选择文件查看内容
                </Text>
              </div>
            </Card>
          )}
        </Col>
      </Row>
    </div>
  );
};

export default FileExplorer; 