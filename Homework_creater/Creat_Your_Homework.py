import pandas as pd
from itertools import product
import os

# ========== 主配置 ==========
data_excel_path = "data.xlsx"         # 原始数据文件
config_excel_path = "config.xlsx"     # Sheet配置文件
split_char = "、"                      # 数据分隔符
placeholder = "@@"                    # 占位符
# ============================

def process_sheet(sheet_name, template_path, output_folder):
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
            for col, value in zip(row_values.keys(), combo):
                content = content.replace(f"{placeholder}{col}{placeholder}", value)
            
            filename = f"行{row_index+1}_{'_'.join(combo)}.json"
            output_path = os.path.join(output_folder, filename)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            total_files += 1

    print(f"✅ Sheet [{sheet_name}] 处理完成，生成 {total_files} 个文件 → {output_folder}")

# 读取配置文件
config_df = pd.read_excel(config_excel_path)

# 遍历所有配置条目
for _, config_row in config_df.iterrows():
    sheet_name = config_row['sheet名称']
    template_path = config_row['模板路径']
    output_folder = config_row['输出目录']
    
    print(f"\n🔄 开始处理 Sheet: {sheet_name}")
    process_sheet(sheet_name, template_path, output_folder)

print("\n所有任务完成！")