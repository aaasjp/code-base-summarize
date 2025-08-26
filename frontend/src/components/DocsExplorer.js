import React, { useState, useEffect, useRef } from 'react';
import { Tree, Card, Typography, Spin, message, Row, Col, Button, Space, Empty } from 'antd';
import { FolderOutlined, FileOutlined, DownloadOutlined, ReloadOutlined, BookOutlined } from '@ant-design/icons';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import 'highlight.js/styles/github.css';
import mermaid from 'mermaid';

// 初始化mermaid配置
mermaid.initialize({
  startOnLoad: false,
  theme: 'default',
  flowchart: {
    useMaxWidth: true,
    htmlLabels: true,
    curve: 'basis'
  }
});

const { Title, Text } = Typography;

// Mermaid组件
const MermaidComponent = ({ chart }) => {
  const elementRef = useRef(null);

  useEffect(() => {
    if (elementRef.current && chart) {
      try {
        mermaid.render(`mermaid-${Date.now()}`, chart).then(({ svg }) => {
          elementRef.current.innerHTML = svg;
        }).catch(error => {
          console.error('Mermaid渲染错误:', error);
          elementRef.current.innerHTML = `<div style="color: red; padding: 10px;">流程图渲染失败: ${error.message}</div>`;
        });
      } catch (error) {
        console.error('Mermaid初始化错误:', error);
        elementRef.current.innerHTML = `<div style="color: red; padding: 10px;">流程图初始化失败: ${error.message}</div>`;
      }
    }
  }, [chart]);

  return <div ref={elementRef} style={{ textAlign: 'center', margin: '20px 0' }} />;
};

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
      
      // 尝试加载项目技术总结文档
      const projectName = fileId; // 使用fileId作为项目名称
      const docsDir = `/Users/ailabuser7-1/Documents/cursor-workspace/code-base-summarize/backend/docs/${projectName}`;
      
      // 检查是否存在技术总结文档
      try {
        const response = await axios.get(`/api/analysis/docs/${fileId}`);
        if (response.data.success && response.data.data.docs.length > 0) {
          const treeNodes = convertToTreeData(response.data.data.docs);
          setTreeData(treeNodes);
        } else {
          // 如果没有文档，显示提示信息
          setTreeData([]);
          message.info('暂无技术总结文档，请先在文件浏览器中点击"项目技术总结"按钮生成文档');
        }
      } catch (error) {
        // 如果接口不存在或失败，显示提示信息
        setTreeData([]);
        message.info('暂无技术总结文档，请先在文件浏览器中点击"项目技术总结"按钮生成文档');
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

  const loadDocContent = async (docPath) => {
    try {
      setContentLoading(true);
      
      const response = await axios.get(`/api/analysis/docs/${fileId}/${docPath}`, {
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

  const handleDocSelect = async (selectedKeys, info) => {
    if (selectedKeys.length === 0) return;
    
    const key = selectedKeys[0];
    const node = info.node;
    
    if (node.isLeaf && node.data) {
      setSelectedDoc(node.data);
      await loadDocContent(key);
    }
  };

  if (!fileId) {
    return (
      <div style={{ textAlign: 'center', padding: 60 }}>
        <BookOutlined style={{ fontSize: 64, color: '#d9d9d9', marginBottom: 24 }} />
        <Title level={3} type="secondary">请选择项目</Title>
        <Text type="secondary" style={{ display: 'block', marginTop: 16 }}>
          请从顶部选择器中选择一个项目来查看技术总结文档
        </Text>
      </div>
    );
  }

  const handleDownloadDoc = async () => {
    if (!selectedDoc) return;
    
    try {
      const response = await axios.get(`/api/analysis/docs/${fileId}/${selectedDoc.full_path}?type=download`, {
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

    // 如果是Markdown内容，使用ReactMarkdown渲染
    if (typeof docContent === 'string') {
      // 检查文件扩展名是否为markdown相关
      const isMarkdownFile = selectedDoc && (
        selectedDoc.name.endsWith('.md') || 
        selectedDoc.name.endsWith('.markdown') ||
        selectedDoc.name.endsWith('.txt') ||
        docContent.includes('# ') ||
        docContent.includes('## ') ||
        docContent.includes('```')
      );

      if (isMarkdownFile) {
        return (
          <div className="doc-preview markdown-content">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              rehypePlugins={[rehypeHighlight]}
              components={{
                // 自定义代码块样式
                code: ({ node, inline, className, children, ...props }) => {
                  const match = /language-(\w+)/.exec(className || '');
                  
                  // 检查是否为mermaid代码块
                  if (!inline && match && match[1] === 'mermaid') {
                    return <MermaidComponent chart={children} />;
                  }
                  
                  return !inline && match ? (
                    <pre className={className} style={{ 
                      backgroundColor: '#f6f8fa', 
                      padding: '16px',
                      borderRadius: '6px',
                      overflow: 'auto'
                    }}>
                      <code className={className} {...props}>
                        {children}
                      </code>
                    </pre>
                  ) : (
                    <code className={className} {...props}>
                      {children}
                    </code>
                  );
                }
              }}
            >
              {docContent}
            </ReactMarkdown>
          </div>
        );
      } else {
        // 普通文本内容
        return (
          <div className="doc-preview">
            <pre style={{ 
              backgroundColor: '#f6f8fa', 
              padding: '16px',
              borderRadius: '6px',
              overflow: 'auto',
              whiteSpace: 'pre-wrap',
              fontFamily: 'Monaco, Menlo, "Ubuntu Mono", monospace',
              fontSize: '14px',
              lineHeight: '1.5'
            }}>
              {docContent}
            </pre>
          </div>
        );
      }
    }

    return null;
  };

  if (loading) {
    return (
      <div className="loading-container">
        <Spin size="large" />
        <Text style={{ marginLeft: 16 }}>正在加载技术总结文档结构...</Text>
      </div>
    );
  }

  return (
    <div>
      <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
        <Col>
          <Title level={2}>项目技术总结</Title>
          <Text type="secondary">
            查看项目技术总结文档，支持Markdown格式
          </Text>
        </Col>
        <Col>
          <Button 
            icon={<ReloadOutlined />}
            onClick={loadDocsStructure}
            size="large"
          >
            刷新文档
          </Button>
        </Col>
      </Row>

      <Row gutter={16} style={{ marginTop: 24 }}>
        <Col span={8}>
          <Card title="技术总结文档" className="docs-tree">
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
                description="暂无技术总结文档" 
                image={Empty.PRESENTED_IMAGE_SIMPLE}
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
                <Button 
                  icon={<DownloadOutlined />} 
                  size="small"
                  onClick={handleDownloadDoc}
                >
                  下载
                </Button>
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
                <FileOutlined style={{ fontSize: 48, color: '#d9d9d9' }} />
                <Text type="secondary" style={{ display: 'block', marginTop: 16 }}>
                  请从左侧选择技术总结文档查看内容
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