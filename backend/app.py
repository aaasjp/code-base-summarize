#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import zipfile
import json
import shutil
import uuid
import asyncio
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import magic
from local_code import LocalCodeClient
from constants import CODE_EXTENSIONS
from llm.qwen_llm import QwenLLM
from prompts.business_logic import BUSINESS_SUMMARY_PROMPT
from prompts.technical_documentation import TECHNICAL_DOCUMENTATION_PROMPT

app = Flask(__name__)
CORS(app)

# 配置
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB限制
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['EXTRACTED_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'extracted')
app.config['TEMP_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp')
app.config['DOCS_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'docs')


def ensure_directories():
    """确保必要的目录存在"""
    directories = [
        app.config['UPLOAD_FOLDER'],
        app.config['EXTRACTED_FOLDER'],
        app.config['TEMP_FOLDER'],
        app.config['DOCS_FOLDER']
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ 目录已创建: {directory}")

def is_zip_file(file_path):
    """检查文件是否为ZIP格式"""
    try:
        mime = magic.from_file(file_path, mime=True)
        return mime in ['application/zip', 'application/x-zip-compressed']
    except Exception:
        # 如果magic库不可用，检查文件扩展名
        return file_path.lower().endswith('.zip')

def get_file_stats(file_path):
    """获取文件统计信息"""
    stat = os.stat(file_path)
    return {
        'size': stat.st_size,
        'modified_at': datetime.fromtimestamp(stat.st_mtime).isoformat(),
        'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat()
    }

def is_code_file(file_path):
    """检查是否为代码文件"""
    return Path(file_path).suffix.lower() in CODE_EXTENSIONS

def get_directory_structure(directory_path, base_path=''):
    """递归获取目录结构"""
    items = []
    
    try:
        for item in os.listdir(directory_path):
            item_path = os.path.join(directory_path, item)
            relative_path = os.path.join(base_path, item)
            
            if os.path.isdir(item_path):
                # 递归处理子目录
                children = get_directory_structure(item_path, relative_path)
                items.append({
                    'name': item,
                    'type': 'directory',
                    'path': relative_path,
                    'children': children
                })
            else:
                # 检查是否为代码文件
                if is_code_file(item_path):
                    stats = get_file_stats(item_path)
                    items.append({
                        'name': item,
                        'type': 'file',
                        'path': relative_path,
                        'extension': Path(item).suffix.lower(),
                        'size': stats['size'],
                        'modified_at': stats['modified_at']
                    })
        
        # 排序：目录在前，文件在后
        items.sort(key=lambda x: (x['type'] != 'directory', x['name'].lower()))
        return items
        
    except Exception as e:
        print(f"读取目录失败: {directory_path}, 错误: {e}")
        return []

def get_all_subdirectories(directory_path):
    """获取目录下的所有子目录，按深度排序（最深层在前）"""
    subdirs = []
    
    def collect_subdirs(path, depth=0):
        try:
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    subdirs.append((item_path, depth))
                    collect_subdirs(item_path, depth + 1)
        except Exception as e:
            print(f"读取目录失败: {path}, 错误: {e}")
    
    collect_subdirs(directory_path)
    
    # 按深度降序排序（最深层在前）
    subdirs.sort(key=lambda x: x[1], reverse=True)
    return [path for path, depth in subdirs]

def generate_documentation_for_directory(directory_path, llm_client):
    """为指定目录生成文档"""
    try:
        # 创建LocalCodeClient实例
        code_client = LocalCodeClient()
        
        # 获取目录结构
        directory_structure = asyncio.run(code_client.get_directory_structure(Path(directory_path)))
        
        # 获取代码内容
        codebase = asyncio.run(code_client.get_all_content_from_directory(Path(directory_path)))
        
        # 生成业务逻辑文档
        business_prompt = BUSINESS_SUMMARY_PROMPT.format(
            directory_structure=directory_structure,
            codebase=codebase
        )
        
        business_doc = llm_client.simple_chat(
            business_prompt,
            "您是一位杰出的软件架构师，专门分析代码库的业务逻辑。请严格按照提供的格式生成文档。"
        )
        
        # 生成技术文档
        technical_prompt = TECHNICAL_DOCUMENTATION_PROMPT.format(
            directory_structure=directory_structure,
            codebase=codebase
        )
        
        technical_doc = llm_client.simple_chat(
            technical_prompt,
            "您是一位杰出的软件架构师和专业技术文档撰写专家。请严格按照提供的格式生成文档。"
        )
        
        return {
            'business_logic': business_doc,
            'technical_doc': technical_doc,
            'directory_structure': directory_structure,
            'codebase': codebase
        }
        
    except Exception as e:
        print(f"生成文档失败: {e}")
        raise e

def save_documentation(docs_data, base_docs_path, directory_name):
    """保存文档到指定目录"""
    try:
        # 创建文档目录
        doc_dir = os.path.join(base_docs_path, directory_name)
        Path(doc_dir).mkdir(parents=True, exist_ok=True)
        
        # 保存业务逻辑文档
        business_file = os.path.join(doc_dir, f"{directory_name}_business_logic.md")
        with open(business_file, 'w', encoding='utf-8') as f:
            f.write(docs_data['business_logic'])
        
        # 保存技术文档
        technical_file = os.path.join(doc_dir, f"{directory_name}_technical_doc.md")
        with open(technical_file, 'w', encoding='utf-8') as f:
            f.write(docs_data['technical_doc'])
        
        return {
            'business_logic_file': business_file,
            'technical_doc_file': technical_file
        }
        
    except Exception as e:
        print(f"保存文档失败: {e}")
        raise e

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'upload_folder': app.config['UPLOAD_FOLDER'],
        'extracted_folder': app.config['EXTRACTED_FOLDER']
    })

@app.route('/api/upload/zip', methods=['POST'])
def upload_zip():
    """上传ZIP文件"""
    try:
        if 'zipFile' not in request.files:
            return jsonify({'error': '请选择要上传的ZIP文件'}), 400
        
        file = request.files['zipFile']
        if file.filename == '':
            return jsonify({'error': '请选择要上传的ZIP文件'}), 400
        
        # 生成唯一文件名
        file_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        file_extension = Path(filename).suffix
        
        if file_extension.lower() != '.zip':
            return jsonify({'error': '只支持上传ZIP格式的文件'}), 400
        
        # 保存文件
        zip_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_id}.zip")
        file.save(zip_path)
        
        # 验证ZIP文件
        if not is_zip_file(zip_path):
            os.remove(zip_path)
            return jsonify({'error': '文件格式错误，请上传有效的ZIP文件'}), 400
        
        # 解压文件
        extracted_dir = os.path.join(app.config['EXTRACTED_FOLDER'], file_id)
        Path(extracted_dir).mkdir(parents=True, exist_ok=True)
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # 检查ZIP文件内容
                file_list = zip_ref.namelist()
                
                if not file_list:
                    os.remove(zip_path)
                    shutil.rmtree(extracted_dir, ignore_errors=True)
                    return jsonify({'error': 'ZIP文件为空'}), 400
                
                # 检查是否包含代码文件
                has_code_files = any(
                    is_code_file(name) for name in file_list 
                    if not name.endswith('/')  # 排除目录
                )
                
                if not has_code_files:
                    os.remove(zip_path)
                    shutil.rmtree(extracted_dir, ignore_errors=True)
                    return jsonify({'error': 'ZIP文件中未找到代码文件'}), 400
                
                # 解压文件
                zip_ref.extractall(extracted_dir)
                
                # 统计文件信息
                total_files = len(file_list)
                code_files = len([name for name in file_list if is_code_file(name) and not name.endswith('/')])
                directories = len([name for name in file_list if name.endswith('/')])
                
                file_stats = get_file_stats(zip_path)
                
                print(f"✅ ZIP文件解析成功: {filename} -> {total_files}个文件, {code_files}个代码文件")
                
                return jsonify({
                    'success': True,
                    'message': 'ZIP文件上传并解析成功',
                    'data': {
                        'file_id': file_id,
                        'original_name': filename,
                        'file_size': file_stats['size'],
                        'extracted_path': extracted_dir,
                        'stats': {
                            'total_files': total_files,
                            'code_files': code_files,
                            'directories': directories,
                            'total_size': file_stats['size']
                        },
                        'uploaded_at': datetime.now().isoformat()
                    }
                })
                
        except zipfile.BadZipFile:
            os.remove(zip_path)
            shutil.rmtree(extracted_dir, ignore_errors=True)
            return jsonify({'error': 'ZIP文件格式错误或已损坏'}), 400
            
    except Exception as e:
        print(f"文件上传处理失败: {e}")
        return jsonify({'error': '文件上传失败', 'message': str(e)}), 500

@app.route('/api/upload/status/<file_id>', methods=['GET'])
def get_upload_status(file_id):
    """获取上传状态"""
    try:
        extracted_path = os.path.join(app.config['EXTRACTED_FOLDER'], file_id)
        
        if not os.path.exists(extracted_path):
            return jsonify({'error': '文件不存在或已被删除'}), 404
        
        stats = get_file_stats(extracted_path)
        
        return jsonify({
            'success': True,
            'data': {
                'file_id': file_id,
                'exists': True,
                'extracted_at': stats['created_at'],
                'last_modified': stats['modified_at']
            }
        })
        
    except Exception as e:
        print(f"获取文件状态失败: {e}")
        return jsonify({'error': '获取文件状态失败'}), 500

@app.route('/api/upload/<file_id>', methods=['DELETE'])
def delete_upload(file_id):
    """删除上传的文件"""
    try:
        zip_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_id}.zip")
        extracted_path = os.path.join(app.config['EXTRACTED_FOLDER'], file_id)
        
        # 删除ZIP文件
        if os.path.exists(zip_path):
            os.remove(zip_path)
        
        # 删除解压目录
        if os.path.exists(extracted_path):
            shutil.rmtree(extracted_path)
        
        return jsonify({
            'success': True,
            'message': '文件删除成功'
        })
        
    except Exception as e:
        print(f"删除文件失败: {e}")
        return jsonify({'error': '删除文件失败'}), 500

@app.route('/api/analysis/structure/<file_id>', methods=['GET'])
def get_project_structure(file_id):
    """获取项目结构"""
    try:
        extracted_path = os.path.join(app.config['EXTRACTED_FOLDER'], file_id)
        
        if not os.path.exists(extracted_path):
            return jsonify({'error': '项目不存在或已被删除'}), 404
        
        # 获取目录结构
        structure = get_directory_structure(extracted_path)
        
        # 统计信息
        total_files = 0
        total_directories = 0
        total_size = 0
        
        def count_items(items):
            nonlocal total_files, total_directories, total_size
            for item in items:
                if item['type'] == 'directory':
                    total_directories += 1
                    if 'children' in item:
                        count_items(item['children'])
                else:
                    total_files += 1
                    total_size += item.get('size', 0)
        
        count_items(structure)
        
        return jsonify({
            'success': True,
            'data': {
                'file_id': file_id,
                'structure': structure,
                'stats': {
                    'total_files': total_files,
                    'total_directories': total_directories,
                    'total_size': total_size
                }
            }
        })
        
    except Exception as e:
        print(f"获取项目结构失败: {e}")
        return jsonify({'error': '获取项目结构失败'}), 500

@app.route('/api/analysis/file/<file_id>', methods=['GET'])
def read_file_content(file_id):
    """读取文件内容"""
    try:
        file_path = request.args.get('filePath')
        
        if not file_path:
            return jsonify({'error': '缺少文件路径参数'}), 400
        
        extracted_path = os.path.join(app.config['EXTRACTED_FOLDER'], file_id)
        full_file_path = os.path.join(extracted_path, file_path)
        
        # 安全检查：确保文件路径在解压目录内
        if not os.path.abspath(full_file_path).startswith(os.path.abspath(extracted_path)):
            return jsonify({'error': '访问被拒绝'}), 403
        
        # 检查文件是否存在
        if not os.path.exists(full_file_path):
            return jsonify({'error': '文件不存在'}), 404
        
        # 检查是否为文件
        if not os.path.isfile(full_file_path):
            return jsonify({'error': '路径不是文件'}), 400
        
        # 检查文件大小（限制为1MB）
        file_size = os.path.getsize(full_file_path)
        if file_size > 1024 * 1024:
            return jsonify({'error': '文件过大，无法读取'}), 413
        
        # 检查文件扩展名
        file_ext = Path(full_file_path).suffix.lower()
        if file_ext not in CODE_EXTENSIONS:
            return jsonify({'error': '不支持的文件类型'}), 400
        
        # 读取文件内容
        try:
            with open(full_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # 如果UTF-8解码失败，尝试其他编码
            try:
                with open(full_file_path, 'r', encoding='gbk') as f:
                    content = f.read()
            except UnicodeDecodeError:
                return jsonify({'error': '文件编码不支持'}), 400
        
        stats = get_file_stats(full_file_path)
        
        return jsonify({
            'success': True,
            'data': {
                'file_id': file_id,
                'file_path': file_path,
                'file_name': Path(full_file_path).name,
                'extension': file_ext,
                'size': file_size,
                'content': content,
                'modified_at': stats['modified_at'],
                'lines': len(content.split('\n'))
            }
        })
        
    except Exception as e:
        print(f"读取文件失败: {e}")
        return jsonify({'error': '读取文件失败'}), 500

@app.route('/api/analysis/search/<file_id>', methods=['GET'])
def search_files(file_id):
    """搜索文件"""
    try:
        query = request.args.get('query')
        extension = request.args.get('extension')
        
        if not query:
            return jsonify({'error': '搜索关键词不能为空'}), 400
        
        extracted_path = os.path.join(app.config['EXTRACTED_FOLDER'], file_id)
        
        if not os.path.exists(extracted_path):
            return jsonify({'error': '项目不存在或已被删除'}), 404
        
        results = []
        
        def search_files_recursive(dir_path, base_path=''):
            try:
                for item in os.listdir(dir_path):
                    item_path = os.path.join(dir_path, item)
                    relative_path = os.path.join(base_path, item)
                    
                    if os.path.isdir(item_path):
                        search_files_recursive(item_path, relative_path)
                    else:
                        file_ext = Path(item).suffix.lower()
                        
                        # 检查扩展名过滤
                        if extension and file_ext != extension.lower():
                            continue
                        
                        # 检查是否为代码文件
                        if file_ext not in CODE_EXTENSIONS:
                            continue
                        
                        # 检查文件名是否匹配
                        if query.lower() in item.lower():
                            stats = get_file_stats(item_path)
                            results.append({
                                'name': item,
                                'path': relative_path,
                                'extension': file_ext,
                                'size': stats['size'],
                                'modified_at': stats['modified_at']
                            })
            except Exception as e:
                print(f"搜索目录失败: {dir_path}, 错误: {e}")
        
        search_files_recursive(extracted_path)
        
        return jsonify({
            'success': True,
            'data': {
                'file_id': file_id,
                'query': query,
                'extension': extension,
                'results': results,
                'total_results': len(results)
            }
        })
        
    except Exception as e:
        print(f"搜索文件失败: {e}")
        return jsonify({'error': '搜索文件失败'}), 500

@app.route('/api/analysis/stats/<file_id>', methods=['GET'])
def get_project_stats(file_id):
    """获取项目统计信息"""
    try:
        extracted_path = os.path.join(app.config['EXTRACTED_FOLDER'], file_id)
        
        if not os.path.exists(extracted_path):
            return jsonify({'error': '项目不存在或已被删除'}), 404
        
        stats = {
            'total_files': 0,
            'total_directories': 0,
            'total_size': 0,
            'extensions': {},
            'largest_files': []
        }
        
        def collect_stats_recursive(dir_path):
            try:
                for item in os.listdir(dir_path):
                    item_path = os.path.join(dir_path, item)
                    
                    if os.path.isdir(item_path):
                        stats['total_directories'] += 1
                        collect_stats_recursive(item_path)
                    else:
                        file_ext = Path(item).suffix.lower()
                        
                        if file_ext in CODE_EXTENSIONS:
                            stats['total_files'] += 1
                            
                            file_size = os.path.getsize(item_path)
                            stats['total_size'] += file_size
                            
                            # 统计扩展名
                            stats['extensions'][file_ext] = stats['extensions'].get(file_ext, 0) + 1
                            
                            # 记录大文件
                            relative_path = os.path.relpath(item_path, extracted_path)
                            stats['largest_files'].append({
                                'name': item,
                                'path': relative_path,
                                'size': file_size,
                                'extension': file_ext
                            })
            except Exception as e:
                print(f"统计目录失败: {dir_path}, 错误: {e}")
        
        collect_stats_recursive(extracted_path)
        
        # 排序扩展名统计
        sorted_extensions = sorted(
            stats['extensions'].items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        stats['extensions'] = [{'extension': ext, 'count': count} for ext, count in sorted_extensions]
        
        # 排序大文件
        stats['largest_files'].sort(key=lambda x: x['size'], reverse=True)
        stats['largest_files'] = stats['largest_files'][:10]  # 只保留前10个
        
        return jsonify({
            'success': True,
            'data': {
                'file_id': file_id,
                'stats': stats
            }
        })
        
    except Exception as e:
        print(f"获取项目统计失败: {e}")
        return jsonify({'error': '获取项目统计失败'}), 500

@app.route('/api/analysis/generate-docs/<file_id>', methods=['POST'])
def generate_documentation(file_id):
    """生成代码文档接口"""
    try:
        # 检查Content-Type
        if not request.is_json:
            return jsonify({
                'error': '请求格式错误',
                'message': '请设置Content-Type为application/json'
            }), 415
        
        # 获取请求参数
        data = request.get_json() or {}
        start_directory = data.get('start_directory', '')  # 可选的起始目录
        
        # 验证文件ID
        extracted_path = os.path.join(app.config['EXTRACTED_FOLDER'], file_id)
        if not os.path.exists(extracted_path):
            return jsonify({'error': '项目不存在或已被删除'}), 404
        
        # 确定起始目录
        if start_directory:
            start_path = os.path.join(extracted_path, start_directory)
            if not os.path.exists(start_path) or not os.path.isdir(start_path):
                return jsonify({'error': '指定的起始目录不存在'}), 400
        else:
            start_path = extracted_path
        
        # 初始化LLM客户端
        try:
            llm_client = QwenLLM()
        except Exception as e:
            return jsonify({'error': f'LLM客户端初始化失败: {str(e)}'}), 500
        
        # 获取所有子目录（按深度降序排序）
        subdirectories = get_all_subdirectories(start_path)
        
        # 添加起始目录本身
        all_directories = [start_path] + subdirectories
        
        results = []
        total_directories = len(all_directories)
        
        for i, directory_path in enumerate(all_directories):
            try:
                directory_name = os.path.basename(directory_path)
                relative_path = os.path.relpath(directory_path, extracted_path)
                
                print(f"📝 正在处理目录 ({i+1}/{total_directories}): {relative_path}")
                
                # 检查目录是否包含代码文件
                code_files = []
                for root, dirs, files in os.walk(directory_path):
                    for file in files:
                        if is_code_file(os.path.join(root, file)):
                            code_files.append(file)
                
                if not code_files:
                    print(f"⚠️ 目录 {relative_path} 不包含代码文件，跳过")
                    continue
                
                # 生成文档
                docs_data = generate_documentation_for_directory(directory_path, llm_client)
                
                # 保存文档
                saved_files = save_documentation(docs_data, app.config['DOCS_FOLDER'], directory_name)
                
                results.append({
                    'directory_name': directory_name,
                    'relative_path': relative_path,
                    'code_files_count': len(code_files),
                    'files': saved_files,
                    'status': 'success'
                })
                
                print(f"✅ 目录 {relative_path} 文档生成完成")
                
            except Exception as e:
                print(f"❌ 处理目录 {directory_path} 失败: {e}")
                results.append({
                    'directory_name': os.path.basename(directory_path),
                    'relative_path': os.path.relpath(directory_path, extracted_path),
                    'error': str(e),
                    'status': 'error'
                })
        
        # 统计结果
        success_count = len([r for r in results if r['status'] == 'success'])
        error_count = len([r for r in results if r['status'] == 'error'])
        
        return jsonify({
            'success': True,
            'message': f'文档生成完成，成功处理 {success_count} 个目录，失败 {error_count} 个',
            'data': {
                'file_id': file_id,
                'start_directory': start_directory or 'root',
                'total_directories': total_directories,
                'success_count': success_count,
                'error_count': error_count,
                'results': results,
                'docs_base_path': app.config['DOCS_FOLDER']
            }
        })
        
    except Exception as e:
        print(f"生成文档接口失败: {e}")
        return jsonify({'error': '生成文档失败', 'message': str(e)}), 500

@app.route('/api/analysis/docs/<file_id>', methods=['GET'])
def get_generated_docs(file_id):
    """获取生成的文档列表"""
    try:
        docs_path = app.config['DOCS_FOLDER']
        
        if not os.path.exists(docs_path):
            return jsonify({
                'success': True,
                'data': {
                    'file_id': file_id,
                    'docs': [],
                    'total_docs': 0
                }
            })
        
        docs = []
        for item in os.listdir(docs_path):
            item_path = os.path.join(docs_path, item)
            if os.path.isdir(item_path):
                doc_files = []
                for file in os.listdir(item_path):
                    if file.endswith('.md'):
                        file_path = os.path.join(item_path, file)
                        stats = get_file_stats(file_path)
                        doc_files.append({
                            'name': file,
                            'path': file_path,
                            'size': stats['size'],
                            'modified_at': stats['modified_at']
                        })
                
                if doc_files:
                    docs.append({
                        'directory_name': item,
                        'files': doc_files
                    })
        
        return jsonify({
            'success': True,
            'data': {
                'file_id': file_id,
                'docs': docs,
                'total_docs': len(docs)
            }
        })
        
    except Exception as e:
        print(f"获取文档列表失败: {e}")
        return jsonify({'error': '获取文档列表失败'}), 500

@app.route('/api/analysis/docs/<file_id>/<directory_name>/<filename>', methods=['GET'])
def download_doc(file_id, directory_name, filename):
    """下载生成的文档"""
    try:
        doc_path = os.path.join(app.config['DOCS_FOLDER'], directory_name, filename)
        
        if not os.path.exists(doc_path):
            return jsonify({'error': '文档不存在'}), 404
        
        # 安全检查：确保文件路径在docs目录内
        if not os.path.abspath(doc_path).startswith(os.path.abspath(app.config['DOCS_FOLDER'])):
            return jsonify({'error': '访问被拒绝'}), 403
        
        return send_from_directory(
            os.path.dirname(doc_path),
            os.path.basename(doc_path),
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        print(f"下载文档失败: {e}")
        return jsonify({'error': '下载文档失败'}), 500

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': '文件过大'}), 413

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': '接口不存在'}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': '服务器内部错误'}), 500


if __name__ == '__main__':
    ensure_directories()
    print("🚀 Python后端服务器启动中...")
    print(f"📁 上传目录: {app.config['UPLOAD_FOLDER']}")
    print(f"📁 解压目录: {app.config['EXTRACTED_FOLDER']}")
    print(f"📁 临时目录: {app.config['TEMP_FOLDER']}")
    print(f"📁 文档目录: {app.config['DOCS_FOLDER']}")
    
    app.run(host='0.0.0.0', port=3001, debug=True) 