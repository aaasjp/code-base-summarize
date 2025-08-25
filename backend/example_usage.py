#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
文档生成功能使用示例
"""

import requests
import json
import time

# 配置
BASE_URL = "http://localhost:3001"
FILE_ID = "172ed93a-50ee-437a-87ac-698dc52aab3c"  # 替换为你的文件ID

def generate_docs_example():
    """生成文档示例"""
    print("🚀 开始生成代码文档...")
    
    # 1. 生成整个项目的文档
    print("\n📝 步骤1: 生成整个项目的文档")
    url = f"{BASE_URL}/api/analysis/generate-docs/{FILE_ID}"
    
    try:
        response = requests.post(url, json={})
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 文档生成成功!")
            print(f"处理目录数: {result['data']['total_directories']}")
            print(f"成功数: {result['data']['success_count']}")
            print(f"失败数: {result['data']['error_count']}")
            
            # 显示处理结果
            for item in result['data']['results']:
                if item['status'] == 'success':
                    print(f"  ✅ {item['relative_path']}: {item['code_files_count']} 个代码文件")
                else:
                    print(f"  ❌ {item['relative_path']}: {item.get('error', '未知错误')}")
        else:
            print(f"❌ 生成文档失败: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return
    
    # 等待文档生成完成
    print("\n⏳ 等待文档生成完成...")
    time.sleep(3)
    
    # 2. 获取生成的文档列表
    print("\n📋 步骤2: 获取生成的文档列表")
    url = f"{BASE_URL}/api/analysis/docs/{FILE_ID}"
    
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 获取文档列表成功!")
            print(f"文档目录数: {result['data']['total_docs']}")
            
            for doc in result['data']['docs']:
                print(f"\n📁 {doc['directory_name']}:")
                for file in doc['files']:
                    print(f"   📄 {file['name']} ({file['size']} bytes)")
        else:
            print(f"❌ 获取文档列表失败: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")

def generate_docs_for_subdirectory_example():
    """为特定子目录生成文档示例"""
    print("\n🎯 为特定子目录生成文档示例...")
    
    # 为 gitsummarize-main 目录生成文档
    url = f"{BASE_URL}/api/analysis/generate-docs/{FILE_ID}"
    data = {
        "start_directory": "gitsummarize-main"
    }
    
    try:
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 子目录文档生成成功!")
            print(f"起始目录: {result['data']['start_directory']}")
            print(f"处理目录数: {result['data']['total_directories']}")
            print(f"成功数: {result['data']['success_count']}")
            print(f"失败数: {result['data']['error_count']}")
        else:
            print(f"❌ 生成文档失败: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")

def download_doc_example():
    """下载文档示例"""
    print("\n📥 下载文档示例...")
    
    # 假设要下载 components 目录的业务逻辑文档
    directory_name = "components"
    filename = "components_business_logic.md"
    
    url = f"{BASE_URL}/api/analysis/docs/{FILE_ID}/{directory_name}/{filename}"
    
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            # 保存文档到本地
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"✅ 文档下载成功: {filename}")
        else:
            print(f"❌ 下载文档失败: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")

if __name__ == "__main__":
    print("📚 代码文档生成功能使用示例")
    print("=" * 50)
    
    # 检查服务器状态
    try:
        health_response = requests.get(f"{BASE_URL}/api/health")
        if health_response.status_code == 200:
            print("✅ 服务器连接正常")
        else:
            print("❌ 服务器响应异常")
            exit(1)
    except Exception as e:
        print(f"❌ 无法连接到服务器: {e}")
        print("请确保后端服务器正在运行 (python app.py)")
        exit(1)
    
    # 运行示例
    generate_docs_example()
    generate_docs_for_subdirectory_example()
    download_doc_example()
    
    print("\n🎉 示例执行完成!")
    print("\n💡 提示:")
    print("1. 确保设置了 DASHSCOPE_API_KEY 环境变量")
    print("2. 文档将保存在 backend/docs/ 目录下")
    print("3. 可以查看 README_DOCS_GENERATION.md 了解更多详情") 