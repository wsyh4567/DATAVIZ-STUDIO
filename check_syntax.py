import ast
try:
    with open('pages/statistics_lab.py', encoding='utf-8') as f:
        ast.parse(f.read(), 'pages/statistics_lab.py')
    print("No errors found.")
except SyntaxError as e:
    print(f"SyntaxError on line {e.lineno}: {e.msg}")
