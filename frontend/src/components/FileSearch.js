import React, { useState } from 'react';
import { Input, Button, Card, List, Typography, Select, Space, message, Spin } from 'antd';
import { SearchOutlined, FileOutlined, DownloadOutlined } from '@ant-design/icons';
import axios from 'axios';

const { Search } = Input;
const { Title, Text } = Typography;
const { Option } = Select;

const FileSearch = ({ fileId }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [extension, setExtension] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const fileExtensions = [
    { value: '.js', label: 'JavaScript (.js)' },
    { value: '.ts', label: 'TypeScript (.ts)' },
    { value: '.jsx', label: 'React JSX (.jsx)' },
    { value: '.tsx', label: 'React TSX (.tsx)' },
    { value: '.py', label: 'Python (.py)' },
    { value: '.java', label: 'Java (.java)' },
    { value: '.cpp', label: 'C++ (.cpp)' },
    { value: '.c', label: 'C (.c)' },
    { value: '.cs', label: 'C# (.cs)' },
    { value: '.php', label: 'PHP (.php)' },
    { value: '.html', label: 'HTML (.html)' },
    { value: '.css', label: 'CSS (.css)' },
    { value: '.json', label: 'JSON (.json)' },
    { value: '.xml', label: 'XML (.xml)' },
    { value: '.md', label: 'Markdown (.md)' },
    { value: '.txt', label: 'Text (.txt)' },
  ];

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      message.warning('请输入搜索关键词');
      return;
    }

    try {
      setLoading(true);
      const params = { query: searchQuery.trim() };
      if (extension) {
        params.extension = extension;
      }

      const response = await axios.get(`/api/analysis/search/${fileId}`, { params });
      
      if (response.data.success) {
        setSearchResults(response.data.data.results);
        if (response.data.data.totalResults === 0) {
          message.info('未找到匹配的文件');
        } else {
          message.success(`找到 ${response.data.data.totalResults} 个文件`);
        }
      } else {
        message.error('搜索失败');
      }
    } catch (error) {
      console.error('搜索错误:', error);
      message.error('搜索失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setSearchQuery('');
    setExtension('');
    setSearchResults([]);
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('zh-CN');
  };

  if (!fileId) {
    return (
      <div style={{ textAlign: 'center', padding: 60 }}>
        <SearchOutlined style={{ fontSize: 64, color: '#d9d9d9', marginBottom: 24 }} />
        <Title level={3} type="secondary">请选择项目</Title>
        <Text type="secondary" style={{ display: 'block', marginTop: 16 }}>
          请从顶部选择器中选择一个项目来搜索文件
        </Text>
      </div>
    );
  }

  return (
    <div>
      <Title level={2}>文件搜索</Title>
      <Text type="secondary">
        在项目中搜索文件名，支持按文件类型过滤
      </Text>

      <Card style={{ marginTop: 24 }}>
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Space wrap>
            <Search
              placeholder="输入文件名关键词"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onSearch={handleSearch}
              style={{ width: 300 }}
              enterButton={<SearchOutlined />}
            />
            
            <Select
              placeholder="选择文件类型"
              value={extension}
              onChange={setExtension}
              allowClear
              style={{ width: 200 }}
            >
              {fileExtensions.map(ext => (
                <Option key={ext.value} value={ext.value}>
                  {ext.label}
                </Option>
              ))}
            </Select>
            
            <Button onClick={handleSearch} type="primary" loading={loading}>
              搜索
            </Button>
            
            <Button onClick={handleClear}>
              清空
            </Button>
          </Space>

          {loading && (
            <div style={{ textAlign: 'center', padding: 20 }}>
              <Spin />
              <Text style={{ marginLeft: 8 }}>正在搜索...</Text>
            </div>
          )}

          {searchResults.length > 0 && (
            <div>
              <Text strong>搜索结果 ({searchResults.length} 个文件):</Text>
              <List
                style={{ marginTop: 16 }}
                dataSource={searchResults}
                renderItem={(item) => (
                  <List.Item
                    actions={[
                      <Button 
                        type="link" 
                        icon={<DownloadOutlined />}
                        onClick={() => {
                          // 这里可以添加下载功能
                          message.info('下载功能开发中...');
                        }}
                      >
                        下载
                      </Button>
                    ]}
                  >
                    <List.Item.Meta
                      avatar={<FileOutlined style={{ fontSize: 20, color: '#1890ff' }} />}
                      title={
                        <Space>
                          <Text strong>{item.name}</Text>
                          <Text type="secondary" style={{ fontSize: 12 }}>
                            {item.extension}
                          </Text>
                        </Space>
                      }
                      description={
                        <Space direction="vertical" size="small">
                          <Text type="secondary" style={{ fontSize: 12 }}>
                            路径: {item.path}
                          </Text>
                          <Space>
                            <Text type="secondary" style={{ fontSize: 12 }}>
                              大小: {formatFileSize(item.size)}
                            </Text>
                            <Text type="secondary" style={{ fontSize: 12 }}>
                              修改时间: {formatDate(item.modified_at)}
                            </Text>
                          </Space>
                        </Space>
                      }
                    />
                  </List.Item>
                )}
              />
            </div>
          )}

          {!loading && searchResults.length === 0 && searchQuery && (
            <div style={{ textAlign: 'center', padding: 40 }}>
              <SearchOutlined style={{ fontSize: 48, color: '#d9d9d9' }} />
              <Text type="secondary" style={{ display: 'block', marginTop: 16 }}>
                未找到匹配的文件
              </Text>
              <Text type="secondary" style={{ fontSize: 12 }}>
                尝试使用不同的关键词或文件类型
              </Text>
            </div>
          )}
        </Space>
      </Card>
    </div>
  );
};

export default FileSearch; 