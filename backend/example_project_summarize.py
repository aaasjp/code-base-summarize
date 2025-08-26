#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
项目技术总结接口使用示例
"""

import requests
import json
import os
from pathlib import Path

def summarize_project(project_path: str, api_base_url: str = "http://localhost:3001"):
    """
    调用项目技术总结接口
    
    Args:
        project_path: 项目目录路径
        api_base_url: API基础URL
    
    Returns:
        接口响应结果
    """
    
    # 验证项目路径
    if not os.path.exists(project_path):
        raise FileNotFoundError(f"项目路径不存在: {project_path}")
    
    if not os.path.isdir(project_path):
        raise ValueError(f"项目路径不是目录: {project_path}")
    
    # 准备请求数据
    url = f"{api_base_url}/api/project/summarize"
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        'project_path': project_path
    }
    
    print(f"🚀 开始分析项目: {project_path}")
    print(f"📡 调用接口: {url}")
    
    try:
        # 发送请求
        response = requests.post(url, headers=headers, json=data, timeout=300)
        
        # 检查响应状态
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ 项目技术总结成功!")
                print(f"📄 文档标题: {result['data']['doc_title']}")
                print(f"📁 文档路径: {result['data']['doc_path']}")
                print(f"📊 代码文件数: {result['data']['code_files_count']}")
                print(f"📏 文档大小: {result['data']['file_size']} 字节")
                return result
            else:
                print(f"❌ 接口返回错误: {result.get('error')}")
                return result
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(f"错误信息: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时，请检查网络连接或增加超时时间")
        return None
    except requests.exceptions.ConnectionError:
        print("❌ 连接错误，请确保后端服务正在运行")
        return None
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None

def main():
    """主函数"""
    
    # 配置
    api_base_url = "http://localhost:3001"
    
    # 示例项目路径（请根据实际情况修改）
    example_projects = [
        # 可以添加多个项目路径进行测试
        # "/path/to/your/project1",
        # "/path/to/your/project2",
    ]
    
    # 如果没有配置示例项目，使用当前目录
    if not example_projects:
        current_dir = os.getcwd()
        print(f"使用当前目录作为示例项目: {current_dir}")
        example_projects = [current_dir]
    
    # 分析每个项目
    for project_path in example_projects:
        print("\n" + "="*60)
        print(f"📂 分析项目: {project_path}")
        print("="*60)
        
        result = summarize_project(project_path, api_base_url)
        
        if result and result.get('success'):
            print("\n📋 分析结果摘要:")
            print(f"   项目名称: {result['data']['project_name']}")
            print(f"   文档标题: {result['data']['doc_title']}")
            print(f"   文档文件: {result['data']['doc_filename']}")
            print(f"   存储目录: {result['data']['docs_dir']}")
            print(f"   代码文件数: {result['data']['code_files_count']}")
            print(f"   文档大小: {result['data']['file_size']} 字节")
            print(f"   创建时间: {result['data']['created_at']}")
        else:
            print("❌ 项目分析失败")
        
        print("\n" + "-"*60)

if __name__ == "__main__":
    main() 