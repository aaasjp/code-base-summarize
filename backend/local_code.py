import asyncio
import logging
from pathlib import Path
from textwrap import dedent
from typing import Dict, List, Optional
import os
from constants import VALID_FILE_EXTENSIONS

logger = logging.getLogger(__name__)

FILE_LIMIT = 100 * 1024  # 100kb


class LocalCodeClient:
    """本地代码目录处理客户端，模仿GitHub客户端的接口"""
    
    def __init__(self, base_path: str = None):
        """
        初始化本地代码客户端
        
        Args:
            base_path: 基础路径，如果为None则使用当前工作目录
        """
        self.base_path = Path(base_path) if base_path else Path.cwd()
        
    async def get_directory_structure_from_path(self, code_path: str) -> str:
        """
        从指定路径获取目录结构
        
        Args:
            code_path: 代码目录路径（相对于base_path或绝对路径）
            
        Returns:
            格式化的目录结构字符串
        """
        full_path = self._resolve_path(code_path)
        return await self.get_directory_structure(full_path)
    
    async def get_all_content_from_path(self, code_path: str) -> str:
        """
        从指定路径获取所有代码内容
        
        Args:
            code_path: 代码目录路径（相对于base_path或绝对路径）
            
        Returns:
            所有代码文件的内容字符串
        """
        full_path = self._resolve_path(code_path)
        return await self.get_all_content_from_directory(full_path)
    
    async def get_directory_structure(self, directory_path: Path) -> str:
        """
        获取目录结构，以树形格式返回
        
        Args:
            directory_path: 目录路径
            
        Returns:
            格式化的目录结构字符串
        """
        if not directory_path.exists():
            raise FileNotFoundError(f"目录不存在: {directory_path}")
        
        if not directory_path.is_dir():
            raise ValueError(f"路径不是目录: {directory_path}")
        
        # 构建目录结构
        structure = self._build_directory_structure(directory_path)
        return self._format_directory_structure(structure)
    
    async def get_all_content_from_directory(self, directory_path: Path) -> str:
        """
        从目录中获取所有代码文件的内容
        
        Args:
            directory_path: 目录路径
            
        Returns:
            所有代码文件内容的格式化字符串
        """
        if not directory_path.exists():
            raise FileNotFoundError(f"目录不存在: {directory_path}")
        
        if not directory_path.is_dir():
            raise ValueError(f"路径不是目录: {directory_path}")
        
        # 获取所有代码文件
        code_files = self._get_code_files(directory_path)
        
        formatted_content = []
        for file_path in code_files:
            try:
                if file_path.stat().st_size > FILE_LIMIT:
                    logger.warning(f"跳过文件: {file_path} 因为文件过大")
                    continue
                
                content = file_path.read_text(encoding='utf-8')
                relative_path = file_path.relative_to(directory_path)
                formatted_content.append(
                    self._get_formatted_content(str(relative_path), content)
                )
            except UnicodeDecodeError:
                logger.warning(f"无法解码文件内容: {file_path}")
                continue
            except Exception as e:
                logger.error(f"读取文件失败 {file_path}: {e}")
                continue
        
        return "\n\n".join(formatted_content)
    
    def _resolve_path(self, code_path: str) -> Path:
        """
        解析路径，支持相对路径和绝对路径
        
        Args:
            code_path: 代码路径
            
        Returns:
            解析后的绝对路径
        """
        path = Path(code_path)
        if path.is_absolute():
            return path
        else:
            return self.base_path / path
    
    def _get_code_files(self, directory_path: Path) -> List[Path]:
        """
        递归获取目录中的所有代码文件
        
        Args:
            directory_path: 目录路径
            
        Returns:
            代码文件路径列表
        """
        code_files = []
        
        for item in directory_path.rglob('*'):
            if item.is_file() and item.suffix.lower() in VALID_FILE_EXTENSIONS:
                code_files.append(item)
        
        return sorted(code_files)
    
    def _build_directory_structure(self, directory_path: Path) -> Dict:
        """
        构建目录结构的嵌套字典
        
        Args:
            directory_path: 目录路径
            
        Returns:
            目录结构字典
        """
        structure = {}
        
        try:
            for item in sorted(directory_path.iterdir()):
                if item.name.startswith('.'):  # 跳过隐藏文件
                    continue
                
                if item.is_dir():
                    # 递归处理子目录
                    children = self._build_directory_structure(item)
                    if children:  # 只添加非空目录
                        structure[item.name] = {
                            'type': 'tree',
                            'path': str(item.relative_to(directory_path)),
                            'children': children
                        }
                elif item.is_file() and item.suffix.lower() in VALID_FILE_EXTENSIONS:
                    # 添加代码文件
                    structure[item.name] = {
                        'type': 'blob',
                        'path': str(item.relative_to(directory_path)),
                        'size': item.stat().st_size
                    }
        except PermissionError:
            logger.warning(f"没有权限访问目录: {directory_path}")
        except Exception as e:
            logger.error(f"构建目录结构时出错 {directory_path}: {e}")
        
        return structure
    
    def _format_directory_structure(
        self, structure: Dict, prefix: str = "", is_last: bool = True
    ) -> str:
        """
        将目录结构格式化为树形字符串
        
        Args:
            structure: 目录结构字典
            prefix: 当前行的前缀
            is_last: 是否为最后一个项目
            
        Returns:
            格式化的目录结构字符串
        """
        if not structure:
            return ""
        
        lines = []
        items = sorted(structure.items())
        
        for i, (name, value) in enumerate(items):
            is_last_item = i == len(items) - 1
            connector = "└── " if is_last_item else "├── "
            
            if value['type'] == 'tree':
                # 目录
                lines.append(f"{prefix}{connector}{name}/")
                new_prefix = prefix + ("    " if is_last_item else "│   ")
                children_str = self._format_directory_structure(
                    value.get('children', {}), new_prefix, is_last_item
                )
                if children_str:
                    lines.append(children_str)
            elif value['type'] == 'blob':
                # 文件
                lines.append(f"{prefix}{connector}{name}")
        
        return "\n".join(lines)
    
    def _get_formatted_content(self, path: str, content: str) -> str:
        """
        格式化文件内容
        
        Args:
            path: 文件路径
            content: 文件内容
            
        Returns:
            格式化的文件内容字符串
        """
        return dedent(
            f"""
=============================================================================
File: {path}
=============================================================================
{content}
"""
        )
    
    async def get_code_stats(self, code_path: str) -> Dict:
        """
        获取代码统计信息
        
        Args:
            code_path: 代码目录路径
            
        Returns:
            统计信息字典
        """
        full_path = self._resolve_path(code_path)
        
        if not full_path.exists():
            raise FileNotFoundError(f"路径不存在: {full_path}")
        
        if not full_path.is_dir():
            raise ValueError(f"路径不是目录: {full_path}")
        
        code_files = self._get_code_files(full_path)
        
        # 按文件类型统计
        file_types = {}
        total_size = 0
        
        for file_path in code_files:
            ext = file_path.suffix.lower()
            size = file_path.stat().st_size
            
            if ext not in file_types:
                file_types[ext] = {'count': 0, 'size': 0}
            
            file_types[ext]['count'] += 1
            file_types[ext]['size'] += size
            total_size += size
        
        return {
            'total_files': len(code_files),
            'total_size': total_size,
            'file_types': file_types,
            'directory_path': str(full_path)
        } 