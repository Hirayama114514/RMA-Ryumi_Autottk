import pandas as pd
from itertools import product
import os
import csv
from io import StringIO
from tkinter import Tk, filedialog  # 👈 新增导入

# ========== 主配置 ==========
config_excel_path = "config.xlsx"     # Sheet配置文件
global_sheet_name = "global"  # 全局变量Sheet名称
split_char = "、"                      # 数据分隔符
placeholder = "@@"                    # 占位符
# ============================

def get_data_file_gui():
    """通过图形界面选择Excel文件"""
    root = Tk()
    root.withdraw()  # 隐藏主窗口
    root.attributes('-topmost', True)  # 确保对话框置顶
    
    file_path = filedialog.askopenfilename(
        title="选择数据文件",
        filetypes=[("Excel文件", "*.xlsx"), ("所有文件", "*.*")],
        defaultextension=".xlsx"
    )
    
    root.destroy()  # 清理Tk对象
    return file_path

def load_global_vars():
    """加载全局变量并转换为字典"""
    try:
        df_global = pd.read_excel(data_excel_path, sheet_name=global_sheet_name)
        return {row['变量名']: str(row['值']) for _, row in df_global.iterrows()}
    except Exception as e:
        print(f"⚠️ 全局变量加载失败: {str(e)}，继续使用空全局变量")
        return {}

def replace_global_placeholders(text, global_vars):
    """用全局变量替换文本中的占位符"""
    for var_name, var_value in global_vars.items():
        text = text.replace(f"{placeholder}{var_name}{placeholder}", var_value)
    return text

def process_sheet(sheet_name, template_path, output_folder, global_vars):
    """处理单个Sheet的核心逻辑"""
    # 读取模板
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
    except FileNotFoundError:
        print(f"⚠️ 模板文件不存在：{template_path}，跳过处理Sheet [{sheet_name}]")
        return

    # 创建输出目录
    os.makedirs(output_folder, exist_ok=True)

    # 读取数据
    df = pd.read_excel(data_excel_path, sheet_name=sheet_name,dtype=str).fillna("")
    total_files = 0

    # 逐行处理
    for row_index, row in df.iterrows():
        row_values = {}
        for col in df.columns:
            cell_values = [v.strip() for v in str(row[col]).split(split_char) if v.strip()]
            row_values[col] = cell_values

        combinations = product(*row_values.values())
        
        for combo in combinations:
            content = template
            # 先替换全局变量
            for var_name, var_value in global_vars.items():
                content = content.replace(f"{placeholder}{var_name}{placeholder}", str(var_value))
            # 再替换行内变量
            for col, value in zip(row_values.keys(), combo):
                content = content.replace(f"{placeholder}{col}{placeholder}", value)
            
            filename = f"行{row_index+1}_{'_'.join(combo)}.json"
            output_path = os.path.join(output_folder, filename)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            total_files += 1

    print(f"✅ Sheet [{sheet_name}] 处理完成，生成 {total_files} 个文件 → {output_folder}")

# 主流程
print("=== 请选择数据文件 ===")
data_excel_path = get_data_file_gui()

if not data_excel_path:  # 用户取消选择
    print("错误：未选择数据文件，程序终止")
    exit()

if not os.path.isfile(data_excel_path):
    print(f"错误：文件 {data_excel_path} 不存在")
    exit()

global_vars = load_global_vars()  # 提前加载全局变量
config_df = pd.read_excel(config_excel_path)  # 读取配置文件

# 遍历所有配置条目
for _, config_row in config_df.iterrows():
    sheet_name = config_row['sheet名称']
    template_path = config_row['模板路径']
    # 👇 动态解析输出目录路径
    raw_output_folder = config_row['输出目录']
    output_folder = replace_global_placeholders(raw_output_folder, global_vars)
    
    print(f"\n🔄 开始处理 Sheet: {sheet_name}")
    process_sheet(sheet_name, template_path, output_folder, global_vars)

print("\n所有任务完成！")