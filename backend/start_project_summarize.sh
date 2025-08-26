#!/bin/bash

# 项目技术总结服务启动脚本

echo "🚀 启动项目技术总结服务..."

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装Python3"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "📦 安装依赖包..."
pip install -r requirements.txt

# 检查环境变量
if [ -z "$DASHSCOPE_API_KEY" ]; then
    echo "⚠️  警告: DASHSCOPE_API_KEY 环境变量未设置"
    echo "请设置通义千问API密钥:"
    echo "export DASHSCOPE_API_KEY='your_api_key_here'"
    echo ""
fi

# 创建必要的目录
echo "📁 创建必要目录..."
mkdir -p uploads extracted temp docs

# 启动服务
echo "🌐 启动Flask服务..."
echo "服务地址: http://localhost:3001"
echo "项目技术总结接口: POST http://localhost:3001/api/project/summarize"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

python3 app.py 