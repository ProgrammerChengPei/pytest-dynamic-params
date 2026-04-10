#!/usr/bin/env python3
"""
批量更新测试文件，删除对已删除功能的所有引用。
需要删除的装饰器：@use_generators、DynRef、@parametrize_test、@parametrize_generator
保留的功能：@param_generator、@parametrize_fixture、pytest.mark.parametrize
"""

import os
import re
from pathlib import Path

# 要处理的目录
test_dir = Path(__file__).parent


# 要删除的功能模式
deleted_patterns = [
    r'from dynamic_params import.*parametrize_test',
    r'from dynamic_params import.*DynRef',
    r'from dynamic_params import.*parametrize_generator',
    r'@parametrize_test',
    r'def test.*parametrize_test',
    r"DynRef\('[^']*'\)",
]


# 要替换的模式
replacements = {
    r'from dynamic_params import.*parametrize_test.*param_generator.*DynRef.*parametrize_generator.*': 'from dynamic_params import param_generator',
    r'from dynamic_params import.*parametrize_test.*param_generator.*DynRef.*': 'from dynamic_params import param_generator',
    r'from dynamic_params import.*parametrize_test.*param_generator.*': 'from dynamic_params import param_generator',
    r'from dynamic_params import.*parametrize_test.*DynRef.*': 'from dynamic_params import param_generator',
    r'from dynamic_params import.*parametrize_test.*': 'from dynamic_params import param_generator',
    r'@parametrize_test\(': '@pytest.mark.parametrize(',
}


def update_test_file(file_path):
    """更新单个测试文件。"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 移除对已删除功能的引用
    for pattern in deleted_patterns:
        content = re.sub(pattern, '', content)
    
    # 应用替换规则
    for old_pattern, new_pattern in replacements.items():
        content = re.sub(old_pattern, new_pattern, content)
    
    # 清理多余的空行
    content = re.sub(r'\n\n\n+', '\n\n', content)
    
    # 写入更新后的内容
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 更新文件: {file_path}")


def main():
    """主函数，批量处理所有测试文件。"""
    test_files = []
    
    # 收集所有需要处理的 .py 文件（排除 __init__.py 和 update_test_files.py）
    for root, dirs, files in os.walk(test_dir):
        for file in files:
            if file.endswith('.py') and file not in ['__init__.py', 'update_test_files.py']:
                file_path = Path(root) / file
                
                # 跳过 test_combo 目录
                if 'test_combo' in str(file_path):
                    continue
                    
                test_files.append(file_path)
    
    print(f"找到 {len(test_files)} 个测试文件需要更新...")
    
    # 更新每个文件
    for file_path in test_files:
        update_test_file(file_path)
    
    print("\n✅ 所有测试文件更新完成！")


if __name__ == "__main__":
    main()