import React, { useState } from 'react';
import { Upload, message, Card, Progress, Button, Space, Typography } from 'antd';
import { InboxOutlined, FileZipOutlined } from '@ant-design/icons';
import axios from 'axios';

const { Dragger } = Upload;
const { Title, Text } = Typography;

const UploadComponent = ({ onUploadSuccess }) => {
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadResult, setUploadResult] = useState(null);

  const uploadProps = {
    name: 'zipFile',
    multiple: false,
    accept: '.zip',
    beforeUpload: (file) => {
      const isZip = file.type === 'application/zip' || file.name.endsWith('.zip');
      if (!isZip) {
        message.error('只能上传ZIP格式的文件！');
        return false;
      }
      
      const isLt100M = file.size / 1024 / 1024 < 100;
      if (!isLt100M) {
        message.error('文件大小不能超过100MB！');
        return false;
      }
      
      return false; // 阻止自动上传
    },
    onChange: (info) => {
      if (info.fileList.length > 0) {
        handleUpload(info.fileList[0].originFileObj);
      }
    },
  };

  const handleUpload = async (file) => {
    if (!file) return;

    setUploading(true);
    setUploadProgress(0);
    setUploadResult(null);

    const formData = new FormData();
    formData.append('zipFile', file);

    try {
      // 模拟上传进度
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      const response = await axios.post('/api/upload/zip', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          setUploadProgress(percentCompleted);
        },
      });

      clearInterval(progressInterval);
      setUploadProgress(100);

      if (response.data.success) {
        message.success('文件上传成功！');
        setUploadResult(response.data.data);
        
        // 延迟调用成功回调，让用户看到进度完成
        setTimeout(() => {
          onUploadSuccess(response.data.data.file_id);
        }, 1000);
      } else {
        message.error(response.data.error || '上传失败');
      }
    } catch (error) {
      console.error('上传错误:', error);
      message.error(error.response?.data?.error || '上传失败，请重试');
    } finally {
      setUploading(false);
    }
  };

  const handleRetry = () => {
    setUploadResult(null);
    setUploadProgress(0);
  };

  return (
    <div className="upload-container">
      <Title level={2}>上传代码项目</Title>
      <Text type="secondary">
        请上传包含代码文件的ZIP压缩包，系统将自动解析项目结构
      </Text>

      {!uploadResult ? (
        <div style={{ marginTop: 24 }}>
          <Dragger {...uploadProps} disabled={uploading}>
            <p className="ant-upload-drag-icon">
              <InboxOutlined />
            </p>
            <p className="ant-upload-text">点击或拖拽ZIP文件到此区域上传</p>
            <p className="ant-upload-hint">
              支持单个ZIP文件，文件大小不超过100MB
            </p>
          </Dragger>

          {uploading && (
            <div style={{ marginTop: 24 }}>
              <Progress percent={uploadProgress} status="active" />
              <Text style={{ marginTop: 8, display: 'block' }}>
                正在上传并解析文件...
              </Text>
            </div>
          )}
        </div>
      ) : (
        <Card style={{ marginTop: 24 }}>
          <div style={{ textAlign: 'center' }}>
            <FileZipOutlined style={{ fontSize: 48, color: '#52c41a', marginBottom: 16 }} />
            <Title level={3} style={{ color: '#52c41a' }}>
              上传成功！
            </Title>
            <Text>文件已成功上传并解析</Text>
            
            <div style={{ marginTop: 24, textAlign: 'left' }}>
              <p><strong>文件名：</strong>{uploadResult.original_name}</p>
              <p><strong>文件大小：</strong>{(uploadResult.file_size / 1024 / 1024).toFixed(2)} MB</p>
              <p><strong>总文件数：</strong>{uploadResult.stats.total_files}</p>
              <p><strong>代码文件数：</strong>{uploadResult.stats.code_files}</p>
              <p><strong>目录数：</strong>{uploadResult.stats.directories}</p>
            </div>

            <Space style={{ marginTop: 24 }}>
              <Button type="primary" onClick={() => onUploadSuccess(uploadResult.file_id)}>
                查看项目结构
              </Button>
              <Button onClick={handleRetry}>
                上传新文件
              </Button>
            </Space>
          </div>
        </Card>
      )}
    </div>
  );
};

export default UploadComponent; 