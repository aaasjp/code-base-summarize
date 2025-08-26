# .gitignore 文件说明

本项目的 `.gitignore` 文件用于过滤掉不需要版本控制的文件和目录。

## 主要过滤规则

### Python 相关
- `__pycache__/` - Python 字节码缓存目录
- `*.pyc`, `*.pyo` - Python 编译文件
- `*.egg-info/` - Python 包信息
- `.env`, `.venv` - 虚拟环境目录
- `venv/`, `env/` - 虚拟环境目录

### Node.js 相关
- `node_modules/` - Node.js 依赖包目录
- `npm-debug.log*` - npm 调试日志
- `yarn-debug.log*` - yarn 调试日志
- `.npm/` - npm 缓存目录

### IDE 和编辑器
- `.vscode/` - Visual Studio Code 配置
- `.idea/` - IntelliJ IDEA 配置
- `*.swp`, `*.swo` - Vim 临时文件
- `*~` - 编辑器备份文件

### 操作系统
- `.DS_Store` - macOS 系统文件
- `Thumbs.db` - Windows 缩略图文件
- `ehthumbs.db` - Windows 缩略图数据库

### 项目特定
- `backend/uploads/` - 上传的文件目录
- `backend/extracted/` - 解压的项目文件目录
- `backend/temp/` - 临时文件目录
- `backend/docs/` - 生成的文档目录
- `*.zip`, `*.tar.gz` - 压缩文件

### API 密钥和配置
- `.env` - 环境变量文件
- `DASHSCOPE_API_KEY` - 通义千问 API 密钥
- `OPENAI_API_KEY` - OpenAI API 密钥
- `GEMINI_API_KEY` - Gemini API 密钥

### 日志和缓存
- `*.log` - 日志文件
- `logs/` - 日志目录
- `.cache/` - 缓存目录
- `cache/` - 缓存目录

### 构建产物
- `build/` - 构建输出目录
- `dist/` - 分发目录
- `out/` - 输出目录

## 为什么需要这些规则

1. **安全性**: 避免将 API 密钥和敏感配置提交到版本控制
2. **性能**: 避免提交大型依赖包和缓存文件
3. **清洁性**: 保持仓库整洁，只包含源代码和必要配置文件
4. **跨平台**: 避免操作系统特定的文件影响其他开发者

## 如何添加新的忽略规则

如果需要添加新的忽略规则，请编辑 `.gitignore` 文件并添加相应的模式。常用的模式包括：

- `*.ext` - 忽略所有 .ext 扩展名的文件
- `directory/` - 忽略整个目录
- `!important.ext` - 不忽略 important.ext 文件（即使匹配其他规则）

## 注意事项

1. 如果文件已经被提交到版本控制，需要先将其从仓库中删除：
   ```bash
   git rm --cached <file_or_directory>
   ```

2. 对于已经被忽略的文件，可以使用以下命令强制添加：
   ```bash
   git add -f <file_or_directory>
   ```

3. 定期检查 `.gitignore` 文件，确保规则仍然适用且没有遗漏重要文件。 