import React, { useState } from 'react';
import { Layout, Menu, theme } from 'antd';
import { FileTextOutlined, UploadOutlined, BarChartOutlined, SearchOutlined, BookOutlined } from '@ant-design/icons';
import UploadComponent from './components/UploadComponent';
import FileExplorer from './components/FileExplorer';
import ProjectStats from './components/ProjectStats';
import FileSearch from './components/FileSearch';
import DocsExplorer from './components/DocsExplorer';

const { Header, Content, Sider } = Layout;

function App() {
  const [currentFileId, setCurrentFileId] = useState(null);
  const [currentView, setCurrentView] = useState('upload');
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();

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
      disabled: !currentFileId,
    },
    {
      key: 'docs',
      icon: <BookOutlined />,
      label: '代码文档',
      disabled: !currentFileId,
    },
    {
      key: 'search',
      icon: <SearchOutlined />,
      label: '文件搜索',
      disabled: !currentFileId,
    },
    {
      key: 'stats',
      icon: <BarChartOutlined />,
      label: '项目统计',
      disabled: !currentFileId,
    },
  ];

  const handleMenuClick = ({ key }) => {
    setCurrentView(key);
  };

  const handleUploadSuccess = (fileId) => {
    setCurrentFileId(fileId);
    setCurrentView('explorer');
  };

  const handleShowDocs = () => {
    setCurrentView('docs');
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
      <Header style={{ display: 'flex', alignItems: 'center' }}>
        <div className="logo">代码项目解析器</div>
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