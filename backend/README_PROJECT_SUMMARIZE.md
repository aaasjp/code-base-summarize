# 项目技术总结接口

## 概述

项目技术总结接口是一个强大的工具，可以对任意项目目录进行深度技术分析，并生成高质量的markdown格式技术总结文档。

## 功能特点

- 🔍 **深度代码分析**: 自动分析项目目录结构和代码内容
- 📝 **智能文档生成**: 使用大模型生成结构化的技术总结文档
- 🏗️ **架构识别**: 自动识别项目的技术架构和核心组件
- 📊 **质量评估**: 评估代码质量和提供改进建议
- 🎯 **智能命名**: 根据内容自动生成合适的文档标题
- 📁 **目录结构保持**: 生成的文档保持与源代码相同的目录结构

## 接口信息

### 接口地址
```
POST /api/project/summarize
```

### 请求格式
```json
{
  "project_path": "/path/to/your/project"
}
```

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| project_path | string | 是 | 项目目录的绝对路径 |

### 响应格式

#### 成功响应
```json
{
  "success": true,
  "message": "项目技术总结文档生成成功",
  "data": {
    "project_path": "/path/to/your/project",
    "project_name": "project-name",
    "doc_title": "项目技术总结文档标题",
    "doc_filename": "项目技术总结文档标题.md",
    "doc_path": "/path/to/docs/project-name/项目技术总结文档标题.md",
    "docs_dir": "/path/to/docs/project-name",
    "file_size": 12345,
    "created_at": "2024-01-01T12:00:00",
    "directory_structure": "项目目录结构...",
    "code_files_count": 100
  }
}
```

#### 错误响应
```json
{
  "error": "错误描述",
  "message": "详细错误信息"
}
```

## 使用示例

### Python 示例

```python
import requests
import json

def summarize_project(project_path: str):
    url = "http://localhost:3001/api/project/summarize"
    headers = {'Content-Type': 'application/json'}
    data = {'project_path': project_path}
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print(f"文档生成成功: {result['data']['doc_path']}")
            return result
        else:
            print(f"生成失败: {result.get('error')}")
    else:
        print(f"请求失败: {response.status_code}")
    
    return None

# 使用示例
result = summarize_project("/path/to/your/project")
```

### cURL 示例

```bash
curl -X POST http://localhost:3001/api/project/summarize \
  -H "Content-Type: application/json" \
  -d '{"project_path": "/path/to/your/project"}'
```

### JavaScript 示例

```javascript
async function summarizeProject(projectPath) {
  try {
    const response = await fetch('http://localhost:3001/api/project/summarize', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        project_path: projectPath
      })
    });
    
    const result = await response.json();
    
    if (result.success) {
      console.log('文档生成成功:', result.data.doc_path);
      return result;
    } else {
      console.error('生成失败:', result.error);
    }
  } catch (error) {
    console.error('请求失败:', error);
  }
  
  return null;
}

// 使用示例
summarizeProject('/path/to/your/project');
```

## 生成的文档内容

技术总结文档包含以下主要内容：

### 1. 项目概述
- 项目简介和主要功能
- 技术栈概览
- 项目规模和复杂度

### 2. 技术架构
- 整体架构设计
- 核心组件分析
- 数据流和交互模式

### 3. 核心功能模块
- 主要功能模块介绍
- 模块职责和实现
- 模块间协作关系

### 4. 关键技术实现
- 关键技术点分析
- 设计模式应用
- 算法和数据结构

### 5. 代码结构分析
- 目录结构分析
- 代码组织方式
- 命名规范和代码风格

### 6. 技术栈详细分析
- 前端技术栈
- 后端技术栈
- 数据库和存储
- 部署和运维

### 7. 开发建议
- 代码质量改进建议
- 架构优化建议
- 技术选型建议
- 性能优化建议

## 支持的文件类型

接口支持分析以下类型的代码文件：

- **前端**: `.js`, `.ts`, `.jsx`, `.tsx`, `.vue`, `.svelte`, `.html`, `.css`, `.scss`, `.sass`
- **后端**: `.py`, `.java`, `.cpp`, `.c`, `.cs`, `.php`, `.rb`, `.go`, `.rs`, `.swift`, `.kt`, `.scala`
- **配置**: `.json`, `.xml`, `.yaml`, `.yml`, `.md`, `.txt`
- **脚本**: `.sh`, `.bat`, `.ps1`, `.sql`
- **其他**: `.r`, `.m`, `.clj`, `.hs`, `.ml`, `.fs`, `.vb`, `.asm`

## 环境要求

### 后端服务要求
- Python 3.7+
- Flask
- 通义千问API密钥 (DASHSCOPE_API_KEY)

### 配置环境变量
```bash
export DASHSCOPE_API_KEY="your_api_key_here"
```

## 注意事项

1. **路径权限**: 确保服务有权限访问指定的项目目录
2. **文件大小**: 单个文件大小限制为100KB
3. **处理时间**: 大型项目可能需要较长的处理时间
4. **API限制**: 注意通义千问API的调用频率限制
5. **存储空间**: 确保有足够的磁盘空间存储生成的文档

## 错误处理

常见错误及解决方案：

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| 项目路径不存在 | 路径错误或权限不足 | 检查路径是否正确，确保有访问权限 |
| LLM客户端初始化失败 | API密钥未配置 | 设置正确的DASHSCOPE_API_KEY环境变量 |
| 请求超时 | 项目过大或网络问题 | 增加超时时间或检查网络连接 |
| 文件编码错误 | 代码文件编码不支持 | 确保代码文件使用UTF-8编码 |

## 扩展功能

### 自定义分析选项
可以通过修改提示词文件 `prompts/technical_summary.py` 来自定义分析内容和格式。

### 批量处理
可以编写脚本批量处理多个项目：

```python
projects = [
    "/path/to/project1",
    "/path/to/project2",
    "/path/to/project3"
]

for project in projects:
    result = summarize_project(project)
    if result:
        print(f"✅ {project} 分析完成")
    else:
        print(f"❌ {project} 分析失败")
```

## 技术支持

如有问题或建议，请参考：
- 项目文档
- 错误日志
- API响应信息 