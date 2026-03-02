"""
将生成的DOCX文件复制到指定目录
"""
import os
import shutil

# 源文件
source_file = "服装销售预测方案.docx"

# 目标目录
target_dir = r"C:\Users\Toxic\Desktop\服装销售预测方案"

# 创建目标目录（如果不存在）
os.makedirs(target_dir, exist_ok=True)

# 目标文件路径
target_file = os.path.join(target_dir, "服装销售预测方案.docx")

# 复制文件
try:
    shutil.copy2(source_file, target_file)
    print(f"文件已成功复制到: {target_file}")
    print(f"文件大小: {os.path.getsize(target_file) / 1024:.2f} KB")
except Exception as e:
    print(f"复制文件时出错: {e}")
