import React, { useState, useEffect } from 'react';
import { Layout, Menu, theme, Select, message } from 'antd';
import { FileTextOutlined, UploadOutlined, BarChartOutlined, SearchOutlined, BookOutlined } from '@ant-design/icons';
import axios from 'axios';
import UploadComponent from './components/UploadComponent';
import FileExplorer from './components/FileExplorer';
import ProjectStats from './components/ProjectStats';
import FileSearch from './components/FileSearch';
import DocsExplorer from './components/DocsExplorer';

const { Header, Content, Sider } = Layout;
const { Option } = Select;

function App() {
  const [currentFileId, setCurrentFileId] = useState(null);
  const [currentView, setCurrentView] = useState('upload');
  const [projects, setProjects] = useState([]);
  const [loadingProjects, setLoadingProjects] = useState(false);
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();

  // 加载项目列表
  const loadProjects = async () => {
    try {
      setLoadingProjects(true);
      const response = await axios.get('/api/projects');
      if (response.data.success) {
        setProjects(response.data.data.projects);
      } else {
        message.error('加载项目列表失败');
      }
    } catch (error) {
      console.error('加载项目列表错误:', error);
      message.error('加载项目列表失败');
    } finally {
      setLoadingProjects(false);
    }
  };

  // 组件挂载时加载项目列表
  useEffect(() => {
    loadProjects();
  }, []);

  const menuItems = [
    {
      key: 'upload',
      icon: <UploadOutlined />,
      label: '上传项目',
    },
    {
      key: 'explorer',
      icon: <FileTextOutlined />,
      label: '文件浏览',
    },
    {
      key: 'docs',
      icon: <BookOutlined />,
      label: '项目技术总结',
    },
    {
      key: 'search',
      icon: <SearchOutlined />,
      label: '文件搜索',
    },
    {
      key: 'stats',
      icon: <BarChartOutlined />,
      label: '项目统计',
    },
  ];

  const handleMenuClick = ({ key }) => {
    setCurrentView(key);
  };

  const handleUploadSuccess = (fileId) => {
    setCurrentFileId(fileId);
    setCurrentView('explorer');
    // 重新加载项目列表
    loadProjects();
  };

  const handleShowDocs = () => {
    setCurrentView('docs');
  };

  const handleProjectChange = (fileId) => {
    setCurrentFileId(fileId);
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

  const renderContent = () => {
    switch (currentView) {
      case 'upload':
        return <UploadComponent onUploadSuccess={handleUploadSuccess} />;
      case 'explorer':
        return <FileExplorer fileId={currentFileId} onShowDocs={handleShowDocs} />;
      case 'docs':
        return <DocsExplorer fileId={currentFileId} />;
      case 'search':
        return <FileSearch fileId={currentFileId} />;
      case 'stats':
        return <ProjectStats fileId={currentFileId} />;
      default:
        return <UploadComponent onUploadSuccess={handleUploadSuccess} />;
    }
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div className="logo">代码项目解析器</div>
        {currentView !== 'upload' && (
          <Select
            placeholder="选择项目"
            value={currentFileId}
            onChange={handleProjectChange}
            style={{ width: 300 }}
            loading={loadingProjects}
            showSearch
            filterOption={(input, option) =>
              option.children.toLowerCase().indexOf(input.toLowerCase()) >= 0
            }
          >
            {projects.map(project => (
              <Option key={project.file_id} value={project.file_id}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span>{project.original_name}</span>
                  <span style={{ fontSize: '12px', color: '#999' }}>
                    {formatFileSize(project.file_size)}
                  </span>
                </div>
              </Option>
            ))}
          </Select>
        )}
      </Header>
      <Layout>
        <Sider width={200} style={{ background: colorBgContainer }}>
          <Menu
            mode="inline"
            defaultSelectedKeys={['upload']}
            selectedKeys={[currentView]}
            style={{ height: '100%', borderRight: 0 }}
            items={menuItems}
            onClick={handleMenuClick}
          />
        </Sider>
        <Layout style={{ padding: '0 24px 24px' }}>
          <Content
            style={{
              padding: 24,
              margin: 0,
              minHeight: 280,
              background: colorBgContainer,
              borderRadius: borderRadiusLG,
            }}
          >
            {renderContent()}
          </Content>
        </Layout>
      </Layout>
    </Layout>
  );
}

export default App; 