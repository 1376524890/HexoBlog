#!/usr/bin/env python3
"""
快速检查问卷星修复版本
"""

import ast
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))


def check_repair():
    """检查修复内容"""
    print("=" * 80)
    print("问卷星修复版本检查")
    print("=" * 80)
    
    # 读取核心文件
    questionnaire_path = Path(__file__).parent / "src/core/questionnaire.py"
    
    try:
        with open(questionnaire_path, 'r', encoding='utf-8') as f:
            code = f.read()
    except FileNotFoundError:
        print(f"✗ 文件不存在：{questionnaire_path}")
        return False
    
    # 检查语法
    try:
        ast.parse(code)
        print("✓ 语法正确")
    except SyntaxError as e:
        print(f"✗ 语法错误：{e}")
        return False
    
    # 检查关键修复内容
    tree = ast.parse(code)
    functions = {node.name: node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
    
    print("\n关键函数检查:")
    required = [
        ('_fill_single_choice', '单选题填充'),
        ('_fill_multiple_choice', '多选题填充'),
        ('_fill_scale_question', '量表题填充'),
        ('_fill_short_answer', '简答题填充'),
        ('submit_questionnaire', '提交问卷'),
        ('js_click', 'JS 点击辅助函数'),
        ('js_click_by_xpath', 'JS 点击 by XPath'),
    ]
    
    all_ok = True
    for func_name, desc in required:
        if func_name in functions:
            print(f"  ✓ {func_name} ({desc})")
        else:
            print(f"  ✗ {func_name} ({desc}) - 缺失")
            all_ok = False
    
    # 检查关键代码模式
    print("\n关键代码模式检查:")
    
    checks = [
        ('execute_script("arguments[0].click();"', 'JavaScript 点击'),
        ('@class=\'jqradio\'', '单选元素选择器'),
        ('@class=\'jqcheckbox\'', '多选元素选择器'),
        ('show_next_page()', '下一页函数'),
        ('submitQuestionnaire()', '提交函数'),
    ]
    
    for pattern, desc in checks:
        if pattern in code:
            print(f"  ✓ {desc}")
        else:
            print(f"  ✗ {desc} - 缺失")
            all_ok = False
    
    print("\n" + "=" * 80)
    if all_ok:
        print("✓ 所有修复内容检查通过!")
        print("=" * 80)
        return True
    else:
        print("✗ 部分检查失败，请查看上方信息")
        print("=" * 80)
        return False


if __name__ == '__main__':
    success = check_repair()
    sys.exit(0 if success else 1)
