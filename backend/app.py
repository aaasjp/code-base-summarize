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
from prompts.technical_summary import TECHNICAL_SUMMARY_PROMPT, DOCUMENT_TITLE_PROMPT
from prompts.file_summary import FILE_SUMMARY_PROMPT, FILE_TITLE_PROMPT

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

@app.route('/api/projects', methods=['GET'])
def get_projects():
    """获取所有已上传的项目列表"""
    try:
        projects = []
        
        # 从uploads目录获取项目信息
        uploads_dir = app.config['UPLOAD_FOLDER']
        if os.path.exists(uploads_dir):
            for filename in os.listdir(uploads_dir):
                if filename.endswith('.zip'):
                    file_id = filename[:-4]  # 移除.zip扩展名
                    file_path = os.path.join(uploads_dir, filename)
                    stats = get_file_stats(file_path)
                    
                    # 检查是否有对应的解压目录
                    extracted_path = os.path.join(app.config['EXTRACTED_FOLDER'], file_id)
                    has_extracted = os.path.exists(extracted_path)
                    
                    # 检查是否有生成的文档
                    docs_path = os.path.join(app.config['DOCS_FOLDER'], file_id)
                    has_docs = os.path.exists(docs_path)
                    
                    projects.append({
                        'file_id': file_id,
                        'original_name': filename,
                        'file_size': stats['size'],
                        'uploaded_at': stats['created_at'],
                        'modified_at': stats['modified_at'],
                        'has_extracted': has_extracted,
                        'has_docs': has_docs
                    })
        
        # 按上传时间倒序排序
        projects.sort(key=lambda x: x['uploaded_at'], reverse=True)
        
        return jsonify({
            'success': True,
            'data': {
                'projects': projects,
                'total_projects': len(projects)
            }
        })
        
    except Exception as e:
        print(f"获取项目列表失败: {e}")
        return jsonify({'error': '获取项目列表失败'}), 500

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



@app.route('/api/project/summarize', methods=['POST'])
def summarize_project():
    """项目代码技术总结接口 - 对每个源代码文件分别进行总结"""
    try:
        # 检查Content-Type
        if not request.is_json:
            return jsonify({
                'error': '请求格式错误',
                'message': '请设置Content-Type为application/json'
            }), 415
        
        # 获取请求参数
        data = request.get_json() or {}
        project_path = data.get('project_path', '')
        
        if not project_path:
            return jsonify({'error': '项目路径不能为空'}), 400
        
        # 验证项目路径
        if not os.path.exists(project_path):
            return jsonify({'error': '项目路径不存在'}), 400
        
        if not os.path.isdir(project_path):
            return jsonify({'error': '项目路径不是目录'}), 400
        
        # 初始化LLM客户端
        try:
            llm_client = QwenLLM()
        except Exception as e:
            return jsonify({'error': f'LLM客户端初始化失败: {str(e)}'}), 500
        
        # 获取所有源代码文件
        code_files = []
        for root, dirs, files in os.walk(project_path):
            for file in files:
                if is_code_file(os.path.join(root, file)):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, project_path)
                    code_files.append({
                        'path': file_path,
                        'relative_path': relative_path,
                        'name': file,
                        'extension': Path(file).suffix.lower()
                    })
        
        if not code_files:
            return jsonify({'error': '项目中未找到源代码文件'}), 400
        
        # 创建总结文档根目录
        project_name = os.path.basename(project_path)
        summary_docs_dir = os.path.join(app.config['DOCS_FOLDER'], project_name)
        Path(summary_docs_dir).mkdir(parents=True, exist_ok=True)
        
        results = []
        success_count = 0
        error_count = 0
        
        print(f"📝 开始处理 {len(code_files)} 个源代码文件...")
        
        # 对每个源代码文件分别进行总结
        for i, code_file in enumerate(code_files):
            try:
                print(f"📄 正在处理文件 ({i+1}/{len(code_files)}): {code_file['relative_path']}")
                
                # 读取源代码文件内容
                try:
                    with open(code_file['path'], 'r', encoding='utf-8') as f:
                        source_code = f.read()
                except UnicodeDecodeError:
                    # 如果UTF-8解码失败，尝试其他编码
                    try:
                        with open(code_file['path'], 'r', encoding='gbk') as f:
                            source_code = f.read()
                    except UnicodeDecodeError:
                        try:
                            with open(code_file['path'], 'r', encoding='latin-1') as f:
                                source_code = f.read()
                        except Exception as e:
                            raise Exception(f"无法读取文件编码: {e}")
                
                # 检查文件内容是否为空
                if not source_code.strip():
                    raise Exception("文件内容为空")
                
                # 限制文件大小，避免过大的文件导致API调用失败
                if len(source_code) > 50000:  # 50KB限制
                    source_code = source_code[:50000] + "\n\n... (文件内容过长，已截断)"
                
                # 生成单个文件的总结提示词
                file_summary_prompt = FILE_SUMMARY_PROMPT.format(
                    file_name=code_file['name'],
                    file_path=code_file['relative_path'],
                    file_extension=code_file['extension'],
                    source_code=source_code
                )
                
                # 调用大模型生成文件总结
                try:
                    file_summary = llm_client.simple_chat(
                        file_summary_prompt,
                        "您是一位杰出的软件工程师和技术文档专家，专门进行代码技术分析和总结。请生成高质量的中文技术文档。"
                    )
                    
                    # 检查响应是否为空
                    if not file_summary or not file_summary.strip():
                        raise Exception("LLM返回的总结内容为空")
                        
                except Exception as llm_error:
                    raise Exception(f"LLM调用失败: {str(llm_error)}")
                
                # 生成文档标题
                try:
                    title_prompt = FILE_TITLE_PROMPT.format(
                        summary_content=file_summary[:500] + "..."
                    )
                    
                    doc_title = llm_client.simple_chat(
                        title_prompt,
                        "您是一位文档命名专家，请生成简洁明了的中文文档标题。"
                    ).strip()
                    
                    # 检查标题是否为空
                    if not doc_title:
                        doc_title = f"{code_file['name']}技术总结"
                        
                except Exception as title_error:
                    print(f"⚠️ 生成标题失败，使用默认标题: {title_error}")
                    doc_title = f"{code_file['name']}技术总结"
                
                # 清理标题
                doc_title = doc_title.replace('#', '').replace('*', '').replace('`', '').strip()
                if not doc_title:
                    doc_title = f"{code_file['name']}技术总结"
                
                # 确保标题是有效的文件名
                import re
                doc_title = re.sub(r'[<>:"/\\|?*]', '_', doc_title)
                
                # 创建对应的目录结构
                relative_dir = os.path.dirname(code_file['relative_path'])
                if relative_dir:
                    target_dir = os.path.join(summary_docs_dir, relative_dir)
                    Path(target_dir).mkdir(parents=True, exist_ok=True)
                else:
                    target_dir = summary_docs_dir
                
                # 保存总结文档
                doc_filename = f"{doc_title}.md"
                doc_path = os.path.join(target_dir, doc_filename)
                
                with open(doc_path, 'w', encoding='utf-8') as f:
                    f.write(file_summary)
                
                # 获取文档统计信息
                doc_stats = get_file_stats(doc_path)
                
                results.append({
                    'file_name': code_file['name'],
                    'file_path': code_file['relative_path'],
                    'doc_title': doc_title,
                    'doc_filename': doc_filename,
                    'doc_path': doc_path,
                    'file_size': doc_stats['size'],
                    'status': 'success'
                })
                
                success_count += 1
                print(f"✅ 文件 {code_file['relative_path']} 总结完成")
                
            except Exception as e:
                import traceback
                error_details = traceback.format_exc()
                print(f"❌ 处理文件 {code_file['relative_path']} 失败: {e}")
                print(f"错误详情: {error_details}")
                results.append({
                    'file_name': code_file['name'],
                    'file_path': code_file['relative_path'],
                    'error': str(e),
                    'error_details': error_details,
                    'status': 'error'
                })
                error_count += 1
        
        print(f"🎉 总结完成！成功处理 {success_count} 个文件，失败 {error_count} 个")
        
        return jsonify({
            'success': True,
            'message': f'项目技术总结完成，成功处理 {success_count} 个文件，失败 {error_count} 个',
            'data': {
                'project_path': project_path,
                'project_name': project_name,
                'summary_docs_dir': summary_docs_dir,
                'total_files': len(code_files),
                'success_count': success_count,
                'error_count': error_count,
                'results': results
            }
        })
        
    except Exception as e:
        print(f"项目技术总结失败: {e}")
        return jsonify({'error': '项目技术总结失败', 'message': str(e)}), 500

@app.route('/api/analysis/docs/<file_id>', methods=['GET'])
def get_generated_docs(file_id):
    """获取项目技术总结文档列表"""
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
        
        # 查找与file_id匹配的项目文档
        project_docs_path = os.path.join(docs_path, file_id)
        if os.path.exists(project_docs_path) and os.path.isdir(project_docs_path):
            # 递归搜索所有子目录中的.md文件
            def find_md_files_recursive(directory, base_path=''):
                files = []
                try:
                    for item in os.listdir(directory):
                        item_path = os.path.join(directory, item)
                        relative_path = os.path.join(base_path, item)
                        
                        if os.path.isdir(item_path):
                            # 递归搜索子目录
                            sub_files = find_md_files_recursive(item_path, relative_path)
                            files.extend(sub_files)
                        elif item.endswith('.md'):
                            # 找到.md文件
                            stats = get_file_stats(item_path)
                            files.append({
                                'name': item,
                                'path': item_path,
                                'relative_path': relative_path,
                                'size': stats['size'],
                                'modified_at': stats['modified_at']
                            })
                except Exception as e:
                    print(f"搜索目录失败: {directory}, 错误: {e}")
                
                return files
            
            # 搜索所有.md文件
            doc_files = find_md_files_recursive(project_docs_path)
            
            if doc_files:
                # 按目录分组
                docs_by_directory = {}
                for file_info in doc_files:
                    dir_path = os.path.dirname(file_info['relative_path'])
                    if dir_path not in docs_by_directory:
                        docs_by_directory[dir_path] = []
                    docs_by_directory[dir_path].append(file_info)
                
                # 转换为API响应格式
                for dir_path, files in docs_by_directory.items():
                    docs.append({
                        'directory_name': dir_path if dir_path else file_id,
                        'directory_path': dir_path,
                        'files': files
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
        print(f"获取项目技术总结文档列表失败: {e}")
        return jsonify({'error': '获取项目技术总结文档列表失败'}), 500

@app.route('/api/analysis/docs/<file_id>/<path:file_path>', methods=['GET'])
def download_doc(file_id, file_path):
    """获取或下载项目技术总结文档"""
    try:
        # 构建完整的文档路径
        doc_path = os.path.join(app.config['DOCS_FOLDER'], file_id, file_path)
        
        if not os.path.exists(doc_path):
            return jsonify({'error': '项目技术总结文档不存在'}), 404
        
        # 安全检查：确保文件路径在docs目录内
        if not os.path.abspath(doc_path).startswith(os.path.abspath(app.config['DOCS_FOLDER'])):
            return jsonify({'error': '访问被拒绝'}), 403
        
        # 检查是否为文件
        if not os.path.isfile(doc_path):
            return jsonify({'error': '路径不是文件'}), 400
        
        # 检查请求头，判断是下载还是读取内容
        accept_header = request.headers.get('Accept', '')
        response_type = request.args.get('type', 'content')  # 默认为读取内容
        
        if response_type == 'download' or 'application/octet-stream' in accept_header:
            # 下载文件
            return send_from_directory(
                os.path.dirname(doc_path),
                os.path.basename(doc_path),
                as_attachment=True,
                download_name=os.path.basename(doc_path)
            )
        else:
            # 读取文件内容
            try:
                with open(doc_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return content, 200, {'Content-Type': 'text/plain; charset=utf-8'}
            except UnicodeDecodeError:
                # 如果UTF-8解码失败，尝试其他编码
                try:
                    with open(doc_path, 'r', encoding='gbk') as f:
                        content = f.read()
                    return content, 200, {'Content-Type': 'text/plain; charset=utf-8'}
                except UnicodeDecodeError:
                    return jsonify({'error': '文件编码不支持'}), 400
        
    except Exception as e:
        print(f"获取项目技术总结文档失败: {e}")
        return jsonify({'error': '获取项目技术总结文档失败'}), 500

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