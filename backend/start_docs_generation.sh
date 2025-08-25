#!/bin/bash

# 代码文档生成功能启动脚本

echo "🚀 启动代码文档生成功能测试..."

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装"
    exit 1
fi

# 检查依赖
echo "📦 检查依赖..."
if ! python3 -c "import flask, openai, requests" 2>/dev/null; then
    echo "📦 安装依赖..."
    pip3 install -r requirements.txt
fi

# 检查环境变量
if [ -z "$DASHSCOPE_API_KEY" ]; then
    echo "⚠️  警告: DASHSCOPE_API_KEY 环境变量未设置"
    echo "请设置您的通义千问API密钥:"
    echo "export DASHSCOPE_API_KEY='your_api_key_here'"
    echo ""
fi

# 启动后端服务器
echo "🌐 启动后端服务器..."
python3 app.py &
SERVER_PID=$!

# 等待服务器启动
echo "⏳ 等待服务器启动..."
sleep 5

# 检查服务器状态
if curl -s http://localhost:3001/api/health > /dev/null; then
    echo "✅ 服务器启动成功"
else
    echo "❌ 服务器启动失败"
    kill $SERVER_PID 2>/dev/null
    exit 1
fi

echo ""
echo "🎯 服务器已启动，可以开始使用文档生成功能:"
echo ""
echo "1. 生成整个项目文档:"
echo "   curl -X POST http://localhost:3001/api/analysis/generate-docs/YOUR_FILE_ID"
echo ""
echo "2. 为特定目录生成文档:"
echo "   curl -X POST http://localhost:3001/api/analysis/generate-docs/YOUR_FILE_ID \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"start_directory\": \"your_subdirectory\"}'"
echo ""
echo "3. 获取文档列表:"
echo "   curl http://localhost:3001/api/analysis/docs/YOUR_FILE_ID"
echo ""
echo "4. 运行测试脚本:"
echo "   python3 test_docs_generation.py"
echo ""
echo "5. 运行使用示例:"
echo "   python3 example_usage.py"
echo ""
echo "按 Ctrl+C 停止服务器"

# 等待用户中断
trap "echo ''; echo '🛑 正在停止服务器...'; kill $SERVER_PID 2>/dev/null; exit 0" INT
wait $SERVER_PID 