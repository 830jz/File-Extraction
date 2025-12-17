import os
import sys
import json
import requests
import tempfile
import mimetypes
import re
from pathlib import Path
from urllib.parse import urlparse, unquote

# 导入通用文件处理工具
from file_utils import get_file_content, read_all_files

# ==========================================
# 飞书工作流专用逻辑
# ==========================================

def extract_content_from_url(url: str) -> str:
    """
    从URL下载文件并提取内容
    
    参数:
        url: 文件的网络地址
        
    返回:
        提取的文件内容字符串
    """
    try:
        # 0. 清理URL (去除可能的反引号、引号、空格)
        url = url.strip().strip('`').strip('"').strip("'").strip()
        
        if not url.startswith(('http://', 'https://')):
            return f"错误: 无效的URL格式: {url}"

        print(f"正在连接 URL: {url}")
        
        # 1. 发起请求，但不立即下载内容
        # 增加 timeout 防止卡死
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()  # 检查请求是否成功
        
        # 2. 确定文件名和扩展名
        # 优先从 Content-Disposition 获取文件名
        content_disposition = response.headers.get('Content-Disposition', '')
        filename = None
        
        if content_disposition:
            # 尝试提取 filename="xyz"
            fname_match = re.search(r'filename="?([^"]+)"?', content_disposition)
            if fname_match:
                filename = fname_match.group(1)
                # 解码文件名（如果是URL编码的）
                filename = unquote(filename)
        
        if not filename:
            # 如果没有 Content-Disposition，从 URL 获取
            parsed_url = urlparse(url)
            path = unquote(parsed_url.path)
            filename = os.path.basename(path)
            
        if not filename:
            filename = "temp_file"
            
        # 3. 检查扩展名，如果没有或不正确，尝试从 Content-Type 推断
        name, ext = os.path.splitext(filename)
        if not ext:
            content_type = response.headers.get('Content-Type', '').split(';')[0].strip()
            print(f"文件名缺少扩展名，尝试根据 Content-Type ({content_type}) 推断...")
            
            # 常用 MIME 类型映射
            mime_map = {
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
                'application/msword': '.doc',
                'application/pdf': '.pdf',
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
                'application/vnd.ms-excel': '.xls',
                'application/vnd.openxmlformats-officedocument.presentationml.presentation': '.pptx',
                'text/plain': '.txt',
                'text/csv': '.csv',
                'application/json': '.json',
                'text/html': '.html',
            }
            
            guess_ext = mime_map.get(content_type)
            if not guess_ext:
                # 尝试使用 mimetypes 库
                guess_ext = mimetypes.guess_extension(content_type)
            
            if guess_ext:
                filename = f"{name}{guess_ext}"
                print(f"推断出的文件名为: {filename}")
            else:
                print("无法推断扩展名，将尝试作为文本文件处理")

        # 4. 创建临时文件并下载
        # 使用 tempfile.mkdtemp 创建临时目录，避免文件冲突
        temp_dir = tempfile.mkdtemp()
        local_file_path = os.path.join(temp_dir, filename)
        
        print(f"正在下载文件...")
        print(f"保存位置: {local_file_path}")
        
        with open(local_file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    
        # 检查文件是否存在且不为空
        if not os.path.exists(local_file_path) or os.path.getsize(local_file_path) == 0:
            return f"错误: 下载文件失败或文件为空: {url}"
            
        # 5. 提取内容
        print("正在提取内容...")
        content = get_file_content(local_file_path)
        
        # 6. 清理临时文件
        try:
            os.remove(local_file_path)
            os.rmdir(temp_dir)
        except Exception as e:
            print(f"警告: 清理临时文件失败: {e}")
            
        return content
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"处理文件时发生错误: {str(e)}"


def main(path):
    """
    根据传入的文件或目录路径自动提取文字内容
    
    参数:
        path: 文件路径、目录路径、URL或包含resourceURL的JSON字符串
        
    返回:
        如果是文件，返回文件内容字符串
        如果是目录，返回包含所有文件内容的格式化字符串
    """
    # 1. 尝试处理 JSON 格式的输入 (飞书附件通常以 JSON 格式传递)
    try:
        if isinstance(path, str):
            # 清理输入字符串，去除可能的首尾空白
            clean_path = path.strip()
            
            # 检查是否看起来像 JSON
            if clean_path.startswith('{') and 'resourceURL' in clean_path:
                try:
                    data = json.loads(clean_path)
                    if isinstance(data, dict) and "resourceURL" in data:
                        url = data["resourceURL"]
                        print(f"检测到 JSON 输入，提取 URL: {url}")
                        return extract_content_from_url(url)
                except json.JSONDecodeError:
                    # 可能是非标准 JSON，尝试简单正则提取
                    pass
                    
            # 2. 尝试直接处理 URL
            if clean_path.startswith(('http://', 'https://')):
                return extract_content_from_url(clean_path)
    except Exception as e:
        print(f"处理输入参数时发生警告: {e}")

    # 3. 处理本地文件或目录
    path_obj = Path(path)
    
    if not path_obj.exists():
        return f"错误: 路径 '{path}' 不存在"
    
    if path_obj.is_file():
        return get_file_content(path_obj)
    elif path_obj.is_dir():
        file_contents = read_all_files(path)
        result = []
        for file_path, content in file_contents.items():
            result.append(f"\n{'='*80}")
            result.append(f"文件: {file_path}")
            result.append(f"{'='*80}")
            result.append(str(content))
            result.append(f"{'='*80}")
        return "\n".join(result)
    else:
        return f"错误: '{path}' 既不是文件也不是目录"
