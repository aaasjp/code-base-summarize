# 项目技术总结接口使用指南

## 快速开始

### 1. 环境准备

确保已安装Python 3.7+，并设置通义千问API密钥：

```bash
export DASHSCOPE_API_KEY="your_api_key_here"
```

### 2. 启动服务

```bash
cd backend
./start_project_summarize.sh
```

或者手动启动：

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

### 3. 使用接口

#### 基本用法

```bash
curl -X POST http://localhost:3001/api/project/summarize \
  -H "Content-Type: application/json" \
  -d '{"project_path": "/path/to/your/project"}'
```

#### Python示例

```python
import requests

def summarize_project(project_path):
    url = "http://localhost:3001/api/project/summarize"
    response = requests.post(url, 
                           headers={'Content-Type': 'application/json'},
                           json={'project_path': project_path})
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print(f"文档生成成功: {result['data']['doc_path']}")
            return result
    return None

# 使用示例
summarize_project("/path/to/your/project")
```

### 4. 测试接口

```bash
cd backend
python3 test_project_summarize.py /path/to/test/project
```

## 接口说明

### 请求格式

- **方法**: POST
- **URL**: `http://localhost:3001/api/project/summarize`
- **Content-Type**: `application/json`

### 请求参数

```json
{
  "project_path": "/absolute/path/to/project"
}
```

### 响应格式

成功响应：
```json
{
  "success": true,
  "message": "项目技术总结文档生成成功",
  "data": {
    "project_path": "/path/to/project",
    "project_name": "project-name",
    "doc_title": "项目技术总结文档标题",
    "doc_filename": "项目技术总结文档标题.md",
    "doc_path": "/path/to/docs/project-name/项目技术总结文档标题.md",
    "docs_dir": "/path/to/docs/project-name",
    "file_size": 12345,
    "created_at": "2024-01-01T12:00:00",
    "code_files_count": 100
  }
}
```

## 功能特点

- 🔍 **智能分析**: 自动分析项目架构和技术栈
- 📝 **高质量文档**: 生成结构化的技术总结文档
- 🎯 **智能命名**: 根据内容自动生成文档标题
- 📁 **目录结构保持**: 文档存储与源代码目录结构一致
- 🚀 **快速处理**: 支持多种编程语言和文件类型

## 支持的文件类型

- **前端**: JS, TS, JSX, TSX, Vue, Svelte, HTML, CSS, SCSS
- **后端**: Python, Java, C++, C#, PHP, Ruby, Go, Rust, Swift
- **配置**: JSON, XML, YAML, Markdown, TXT
- **脚本**: Shell, Batch, PowerShell, SQL
- **其他**: R, MATLAB, Clojure, Haskell等

## 注意事项

1. 确保项目路径存在且有读取权限
2. 单个文件大小限制为100KB
3. 大型项目处理可能需要较长时间
4. 需要有效的通义千问API密钥

## 故障排除

### 常见问题

1. **API密钥错误**: 检查DASHSCOPE_API_KEY环境变量
2. **路径权限**: 确保服务有权限访问项目目录
3. **网络超时**: 增加请求超时时间
4. **文件编码**: 确保代码文件使用UTF-8编码

### 获取帮助

- 查看错误日志
- 检查API响应信息
- 参考完整文档：`README_PROJECT_SUMMARIZE.md` 