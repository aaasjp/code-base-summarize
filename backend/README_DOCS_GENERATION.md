# 代码文档生成功能说明

## 功能概述

本功能实现了从目录地址开始，自底向上地分析代码结构，并利用大模型生成业务逻辑和技术文档的功能。

## 核心特性

- **自底向上分析**: 从最深层子目录开始，逐层向上分析代码结构
- **智能文档生成**: 利用通义千问大模型生成高质量的业务逻辑和技术文档
- **结构化存储**: 按照原有代码目录结构存储生成的markdown文档
- **灵活配置**: 支持指定起始目录，可以针对特定子目录生成文档

## 接口说明

### 1. 生成文档接口

**接口地址**: `POST /api/analysis/generate-docs/<file_id>`

**功能**: 为指定项目生成代码文档

**请求参数**:
```json
{
  "start_directory": "可选，指定起始目录，默认为项目根目录"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "文档生成完成，成功处理 5 个目录，失败 0 个",
  "data": {
    "file_id": "172ed93a-50ee-437a-87ac-698dc52aab3c",
    "start_directory": "root",
    "total_directories": 5,
    "success_count": 5,
    "error_count": 0,
    "results": [
      {
        "directory_name": "components",
        "relative_path": "gitsummarize-main/src/components",
        "code_files_count": 3,
        "files": {
          "business_logic_file": "/path/to/docs/components/components_business_logic.md",
          "technical_doc_file": "/path/to/docs/components/components_technical_doc.md"
        },
        "status": "success"
      }
    ],
    "docs_base_path": "/path/to/docs"
  }
}
```

### 2. 获取文档列表接口

**接口地址**: `GET /api/analysis/docs/<file_id>`

**功能**: 获取已生成的文档列表

**响应示例**:
```json
{
  "success": true,
  "data": {
    "file_id": "172ed93a-50ee-437a-87ac-698dc52aab3c",
    "docs": [
      {
        "directory_name": "components",
        "files": [
          {
            "name": "components_business_logic.md",
            "path": "/path/to/docs/components/components_business_logic.md",
            "size": 2048,
            "modified_at": "2024-01-01T12:00:00"
          },
          {
            "name": "components_technical_doc.md",
            "path": "/path/to/docs/components/components_technical_doc.md",
            "size": 3072,
            "modified_at": "2024-01-01T12:00:00"
          }
        ]
      }
    ],
    "total_docs": 1
  }
}
```

### 3. 下载文档接口

**接口地址**: `GET /api/analysis/docs/<file_id>/<directory_name>/<filename>`

**功能**: 下载指定的文档文件

**参数**:
- `file_id`: 项目ID
- `directory_name`: 目录名称
- `filename`: 文件名

## 工作流程

1. **目录扫描**: 从指定起始目录开始，递归扫描所有子目录
2. **深度排序**: 按目录深度降序排序，确保最深层目录优先处理
3. **代码分析**: 对每个目录进行代码文件识别和内容提取
4. **文档生成**: 使用大模型生成业务逻辑和技术文档
5. **文件存储**: 按照目录结构保存markdown文档

## 文档类型

### 业务逻辑文档 (`*_business_logic.md`)
- 组件名称和目的
- 关键职责和工作流程
- 输入输出和依赖关系
- 业务规则和约束
- 设计考虑

### 技术文档 (`*_technical_doc.md`)
- 高级架构概览
- 组件分解和类函数文档
- 使用示例和配置说明
- 设计模式和扩展指南

## 文件命名规则

生成的文档文件按照以下规则命名：
- 业务逻辑文档: `{目录名}_business_logic.md`
- 技术文档: `{目录名}_technical_doc.md`

## 目录结构

```
backend/
├── docs/                    # 生成的文档存储目录
│   ├── components/          # 按目录名组织
│   │   ├── components_business_logic.md
│   │   └── components_technical_doc.md
│   ├── utils/
│   │   ├── utils_business_logic.md
│   │   └── utils_technical_doc.md
│   └── ...
```

## 使用示例

### 1. 生成整个项目的文档
```bash
curl -X POST http://localhost:3001/api/analysis/generate-docs/172ed93a-50ee-437a-87ac-698dc52aab3c
```

### 2. 为特定子目录生成文档
```bash
curl -X POST http://localhost:3001/api/analysis/generate-docs/172ed93a-50ee-437a-87ac-698dc52aab3c \
  -H "Content-Type: application/json" \
  -d '{"start_directory": "gitsummarize-main/src/components"}'
```

### 3. 获取文档列表
```bash
curl http://localhost:3001/api/analysis/docs/172ed93a-50ee-437a-87ac-698dc52aab3c
```

### 4. 下载文档
```bash
curl http://localhost:3001/api/analysis/docs/172ed93a-50ee-437a-87ac-698dc52aab3c/components/components_business_logic.md \
  -o components_business_logic.md
```

## 测试

运行测试脚本验证功能：
```bash
cd backend
python test_docs_generation.py
```

## 注意事项

1. **API密钥**: 确保设置了 `DASHSCOPE_API_KEY` 环境变量
2. **文件大小**: 单个代码文件限制为100KB
3. **处理时间**: 大项目可能需要较长时间处理
4. **错误处理**: 接口会跳过不包含代码文件的目录
5. **并发限制**: 建议避免同时处理多个大项目

## 错误码说明

- `400`: 请求参数错误或指定目录不存在
- `404`: 项目不存在或已被删除
- `500`: 服务器内部错误或LLM调用失败 