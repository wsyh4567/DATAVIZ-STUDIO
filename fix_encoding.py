# -*- coding: utf-8 -*-
"""Batch fix Python file encoding issues"""

import os
import sys
import io

# Set stdout to UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def fix_file_encoding(filepath):
    """Add UTF-8 encoding declaration to Python files"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if encoding declaration already exists
        if content.startswith('# -*- coding:') or content.startswith('# coding:'):
            print(f"Skip {filepath} (already has encoding)")
            return False

        # Add encoding declaration
        new_content = '# -*- coding: utf-8 -*-\n' + content

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)

        print(f"Fixed {filepath}")
        return True
    except Exception as e:
        print(f"Error {filepath}: {e}")
        return False

def main():
    """Scan and fix all Python files"""
    root_dir = os.path.dirname(os.path.abspath(__file__))
    fixed_count = 0

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip virtual environment and cache directories
        if 'venv' in dirpath or '__pycache__' in dirpath or '.git' in dirpath:
            continue

        for filename in filenames:
            if filename.endswith('.py') and filename != 'fix_encoding.py':
                filepath = os.path.join(dirpath, filename)
                if fix_file_encoding(filepath):
                    fixed_count += 1

    print(f"\nDone! Fixed {fixed_count} files")

if __name__ == '__main__':
    main()
