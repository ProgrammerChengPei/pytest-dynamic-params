#!/usr/bin/env python3
"""
快速修复所有测试文件，删除已删除功能的引用。
"""

import os
import re


# 要修复的模式和替换规则
fix_rules = [
    # 更新导入语句
    (r'from dynamic_params import.*', 'from dynamic_params import param_generator'),
    
    # 替换 @parametrize_test 为 @pytest.mark.parametrize
    (r'@parametrize_test\(', '@pytest.mark.parametrize('),
    
    # 删除其他已删除功能的引用
    (r',?\s*parametrize_test', ''),
    (r',?\s*DynRef', ''),
    (r',?\s*parametrize_generator', ''),
    (r'\s*use_generators,?', ''),
]


def fix_file(file_path):
    """修复单个文件。"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 应用所有修复规则
        for pattern, replacement in fix_rules:
            content = re.sub(pattern, replacement, content)
        
        # 确保正确导入 pytest
        if 'import pytest' not in content and 'pytest.mark.parametrize' in content:
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('import') or line.startswith('from'):
                    # 在第一个导入语句后插入 pytest 导入
                    lines.insert(i + 1, 'import pytest')
                    content = '\n'.join(lines)
                    break
        
        # 清理多余的空行和逗号
        content = re.sub(r',\s*,', ',', content)  # 删除连续的逗号
        content = re.sub(r'^\s*\n', '', content, flags=re.MULTILINE)  # 删除开头的空行
        
        # 如果内容有变化，则写入文件
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ 已修复: {file_path}")
            
    except Exception as e:
        print(f"❌ 修复失败 {file_path}: {e}")


def main():
    """主函数：批量修复文件。"""
    test_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 需要修复的文件列表（通过前面检测得到）
    files_to_fix = [
        os.path.join(test_dir, 'compatibility', 'test_pytest_asyncio.py'),
        os.path.join(test_dir, 'compatibility', 'test_pytest_bdd.py'),
        os.path.join(test_dir, 'compatibility', 'test_pytest_cov.py'),
        os.path.join(test_dir, 'compatibility', 'test_version_compatibility.py'),
        os.path.join(test_dir, 'compatibility', 'test_xdist.py'),
        os.path.join(test_dir, 'functional', 'test_basic_functionality.py'),
        os.path.join(test_dir, 'functional', 'test_performance_caching.py'),
        os.path.join(test_dir, 'functional', 'test_real_world_scenarios.py'),
        os.path.join(test_dir, 'performance', 'test_benchmarks.py'),
        os.path.join(test_dir, 'performance', 'test_concurrency.py'),
        os.path.join(test_dir, 'performance', 'test_large_scale_parametrization.py'),
        os.path.join(test_dir, 'performance', 'test_memory_efficiency.py'),
        os.path.join(test_dir, 'unit', 'test_decorators.py'),
        os.path.join(test_dir, 'unit', 'test_decorators_comprehensive.py'),
        os.path.join(test_dir, 'unit', 'test_decorators_extended.py'),
        os.path.join(test_dir, 'unit', 'test_errors.py'),
        os.path.join(test_dir, 'unit', 'test_low_coverage_modules.py'),
        os.path.join(test_dir, 'unit', 'test_module_structure.py'),
        os.path.join(test_dir, 'unit', 'test_parametrize_fixture_decorator.py'),
        os.path.join(test_dir, 'unit', 'test_processor.py'),
        os.path.join(test_dir, 'unit', 'test_public_api.py'),
        os.path.join(test_dir, 'unit', 'test_public_api_imports.py'),
    ]
    
    print(f"开始修复 {len(files_to_fix)} 个文件...")
    
    # 修复每个文件
    for file_path in files_to_fix:
        fix_file(file_path)
    
    print("\n✅ 所有文件修复完成！")


if __name__ == "__main__":
    main()