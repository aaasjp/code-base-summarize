#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import json
from pathlib import Path
from local_code import LocalCodeClient

async def main():
    """使用示例：演示如何使用LocalCodeClient"""
    
    # 初始化客户端，可以指定基础路径
    # 如果不指定，将使用当前工作目录
    client = LocalCodeClient()
    
    # 示例1：获取当前目录的结构
    print("=== 示例1：获取当前目录结构 ===")
    try:
        directory_structure = await client.get_directory_structure_from_path(".")
        print("目录结构:")
        print(directory_structure)
    except Exception as e:
        print(f"获取目录结构失败: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # 示例2：获取backend目录的代码内容
    print("=== 示例2：获取backend目录的代码内容 ===")
    try:
        code_content = await client.get_all_content_from_path("backend")
        print(f"代码内容长度: {len(code_content)} 字符")
        print("前1000个字符预览:")
        print(code_content[:1000] + "..." if len(code_content) > 1000 else code_content)
    except Exception as e:
        print(f"获取代码内容失败: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # 示例3：获取代码统计信息
    print("=== 示例3：获取代码统计信息 ===")
    try:
        stats = await client.get_code_stats("backend")
        print("代码统计信息:")
        print(json.dumps(stats, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"获取统计信息失败: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # 示例4：获取特定子目录的结构
    print("=== 示例4：获取frontend目录结构 ===")
    try:
        frontend_structure = await client.get_directory_structure_from_path("frontend")
        print("Frontend目录结构:")
        print(frontend_structure)
    except Exception as e:
        print(f"获取frontend目录结构失败: {e}")

def create_prompt_with_codebase(directory_structure: str, code_content: str) -> str:
    """
    创建包含代码库信息的prompt
    
    Args:
        directory_structure: 目录结构字符串
        code_content: 代码内容字符串
        
    Returns:
        格式化的prompt字符串
    """
    prompt = f"""
请分析以下代码库：

## 目录结构
```
{directory_structure}
```

## 代码内容
{code_content}

## 分析要求
1. 请分析这个代码库的整体架构
2. 识别主要的模块和功能
3. 分析代码质量和可维护性
4. 提供改进建议

请用中文回答。
"""
    return prompt

async def generate_codebase_analysis(code_path: str = "."):
    """
    生成代码库分析的完整示例
    
    Args:
        code_path: 要分析的代码路径
    """
    client = LocalCodeClient()
    
    try:
        # 获取目录结构
        print("正在获取目录结构...")
        directory_structure = await client.get_directory_structure_from_path(code_path)
        
        # 获取代码内容
        print("正在获取代码内容...")
        code_content = await client.get_all_content_from_path(code_path)
        
        # 生成prompt
        prompt = create_prompt_with_codebase(directory_structure, code_content)
        
        print("=== 生成的Prompt ===")
        print(prompt)
        
        # 保存到文件
        output_file = Path("codebase_analysis_prompt.txt")
        output_file.write_text(prompt, encoding='utf-8')
        print(f"\nPrompt已保存到: {output_file}")
        
    except Exception as e:
        print(f"生成代码库分析失败: {e}")

if __name__ == "__main__":
    # 运行基本示例
    asyncio.run(main())
    
    # 运行完整的代码库分析示例
    print("\n" + "="*50)
    print("运行完整的代码库分析示例...")
    asyncio.run(generate_codebase_analysis(".")) 