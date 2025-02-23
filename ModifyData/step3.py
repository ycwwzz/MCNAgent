
"""
由于灰臀数据批量导入只允许每次500条数据批量导入，这里把根据视频导出的3k+条数据，然后切分出来
"""

import pandas as pd
import os
# 读取Excel文件
input_file = '../xhs/biji/daren_urls.xlsx'  # 输入文件名
df = pd.read_excel(input_file)

# 每个文件的行数
chunk_size = 500
folder_path = "../xhs/biji"
# 计算需要拆分的文件数量
num_chunks = len(df) // chunk_size + (1 if len(df) % chunk_size != 0 else 0)

# 拆分并保存
for i in range(num_chunks):
    start_idx = i * chunk_size
    end_idx = start_idx + chunk_size
    chunk_df = df[start_idx:end_idx]

    output_file_path = f'output_part_{i + 1}.xlsx'

    output_file = os.path.join(folder_path, output_file_path)
    if not os.path.exists(output_file):
        os.system(r"touch {}".format(output_file))  # 调用系统命令行来创建文件
    chunk_df.to_excel(output_file, index=False)



print("拆分完成！")