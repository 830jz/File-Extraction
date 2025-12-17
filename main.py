import sys
from pathlib import Path

# 导入通用文件处理工具
from file_utils import get_file_content, read_all_files

def extract_content(path: str) -> str:
    """
    根据传入的文件或目录路径自动提取文字内容
    
    参数:
        path: 文件路径或目录路径
        
    返回:
        如果是文件，返回文件内容字符串
        如果是目录，返回包含所有文件内容的格式化字符串
    """
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


def main():
    """
    主函数：演示如何使用 extract_content 函数
    """
    if len(sys.argv) > 1:
        # 如果命令行提供了路径，则处理该路径
        target_path = sys.argv[1]
        print(f"正在提取 '{target_path}' 的内容...\n")
        print(extract_content(target_path))
    else:
        # 默认行为：交互式输入或处理当前目录
        print("请输入要提取内容的文件或目录路径 (直接回车默认处理当前目录):")
        user_input = input().strip()
        
        target_path = user_input if user_input else "."
        
        print(f"\n正在提取 '{target_path}' 的内容...\n")
        content = extract_content(target_path)
        print(content)
        
        # 可选：保存结果
        if len(content) > 100:  # 如果内容较多，提示保存
            save_to_file = input("\n内容较多，是否保存到文件？(y/n): ").lower()
            if save_to_file == 'y':
                output_file = "extracted_content.txt"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"结果已保存到 {output_file}")


if __name__ == "__main__":
    main()
