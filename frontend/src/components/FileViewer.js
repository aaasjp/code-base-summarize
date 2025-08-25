import React from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Card, Typography, Tag, Space } from 'antd';
import { FileTextOutlined, CodeOutlined } from '@ant-design/icons';

const { Text } = Typography;

const FileViewer = ({ content, fileName, extension, lines }) => {
  // 根据文件扩展名确定语言
  const getLanguage = (ext) => {
    const languageMap = {
      '.js': 'javascript',
      '.jsx': 'javascript',
      '.ts': 'typescript',
      '.tsx': 'typescript',
      '.py': 'python',
      '.java': 'java',
      '.cpp': 'cpp',
      '.c': 'c',
      '.cs': 'csharp',
      '.php': 'php',
      '.rb': 'ruby',
      '.go': 'go',
      '.rs': 'rust',
      '.swift': 'swift',
      '.kt': 'kotlin',
      '.scala': 'scala',
      '.html': 'html',
      '.css': 'css',
      '.scss': 'scss',
      '.sass': 'sass',
      '.vue': 'vue',
      '.svelte': 'svelte',
      '.json': 'json',
      '.xml': 'xml',
      '.yaml': 'yaml',
      '.yml': 'yaml',
      '.md': 'markdown',
      '.txt': 'text',
      '.sh': 'bash',
      '.bat': 'batch',
      '.ps1': 'powershell',
      '.sql': 'sql',
      '.r': 'r',
      '.m': 'matlab',
      '.clj': 'clojure',
      '.hs': 'haskell',
      '.ml': 'ocaml',
      '.fs': 'fsharp',
      '.vb': 'vbnet',
      '.asm': 'assembly'
    };
    
    return languageMap[ext.toLowerCase()] || 'text';
  };

  const language = getLanguage(extension);

  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        <Space>
          <FileTextOutlined />
          <Text strong>{fileName}</Text>
          <Tag color="blue">{extension}</Tag>
          <Tag color="green">{language}</Tag>
          <Text type="secondary">{lines} 行</Text>
        </Space>
      </div>
      
      <Card 
        size="small" 
        style={{ 
          backgroundColor: '#f8f9fa',
          border: '1px solid #e9ecef'
        }}
      >
        <SyntaxHighlighter
          language={language}
          style={tomorrow}
          customStyle={{
            margin: 0,
            padding: '16px',
            fontSize: '14px',
            lineHeight: '1.5',
            backgroundColor: 'transparent',
            border: 'none'
          }}
          showLineNumbers={true}
          wrapLines={true}
        >
          {content}
        </SyntaxHighlighter>
      </Card>
    </div>
  );
};

export default FileViewer; 