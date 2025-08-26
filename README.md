# 代码项目解析器

一个前后端分离的代码项目zip包上传解析系统，支持上传、解析和分析代码项目。

## 功能特性

- 📦 **ZIP文件上传**: 支持拖拽上传ZIP格式的代码项目
- 🔍 **项目结构解析**: 自动解析ZIP包中的目录结构
- 📁 **文件浏览器**: 树形结构展示项目文件
- 🔎 **文件搜索**: 支持按文件名和类型搜索
- 📊 **项目统计**: 详细的文件类型和大小统计
- 📚 **代码文档生成**: 自动生成业务逻辑和技术文档
- 💻 **代码高亮**: 支持多种编程语言的语法高亮
- 📱 **响应式设计**: 现代化的用户界面

## 技术栈

### 后端 (Python)
- **Flask**: Web框架
- **Flask-CORS**: 跨域支持
- **python-magic**: 文件类型检测
- **zipfile**: ZIP文件处理
- **pathlib**: 路径处理

### 前端 (React)
- **React 18**: 前端框架
- **Ant Design**: UI组件库
- **Axios**: HTTP客户端
- **React Router**: 路由管理
- **React Syntax Highlighter**: 代码高亮

## 快速开始

### 环境要求

- Node.js 16+
- Python 3.8+
- npm 或 yarn

### 安装依赖

1. 安装根项目依赖：
```bash
npm install
```

2. 安装前端依赖：
```bash
cd frontend
npm install
```

3. 安装后端依赖：
```bash
cd backend
pip install -r requirements.txt
```
在mac上还需要 brew install libmagic

### 启动项目

#### 方式一：分别启动

1. 启动后端服务：
```bash
cd backend
python app.py
```

2. 启动前端服务：
```bash
cd frontend
npm start
```

#### 方式二：一键启动

```bash
npm run dev
```

### 访问应用

- 前端: http://localhost:3000
- 后端API: http://localhost:3001

## 使用说明

### 1. 上传项目
1. 将代码项目打包成ZIP文件
2. 在前端页面拖拽或点击上传ZIP文件
3. 系统自动验证文件格式并解析

### 2. 浏览文件
1. 上传成功后自动跳转到文件浏览器
2. 左侧显示项目目录结构
3. 点击文件可在右侧查看内容

### 3. 搜索文件
1. 切换到"文件搜索"页面
2. 输入文件名关键词
3. 可选择特定文件类型过滤

### 4. 查看统计
1. 切换到"项目统计"页面
2. 查看文件类型分布、大小统计等信息

### 5. 生成代码文档
1. 在"文件浏览"页面点击"生成代码文档"按钮
2. 等待文档生成完成
3. 切换到"代码文档"页面查看生成的文档
4. 支持按目录结构浏览和下载文档

## 支持的文件类型

- **JavaScript**: .js, .jsx
- **TypeScript**: .ts, .tsx
- **Python**: .py
- **Java**: .java
- **C/C++**: .c, .cpp
- **C#**: .cs
- **PHP**: .php
- **HTML/CSS**: .html, .css, .scss, .sass
- **Vue/Svelte**: .vue, .svelte
- **配置文件**: .json, .xml, .yaml, .yml
- **文档**: .md, .txt
- **脚本**: .sh, .bat, .ps1
- **数据库**: .sql
- **其他**: .go, .rs, .swift, .kt, .rb 等

## 许可证

MIT License 