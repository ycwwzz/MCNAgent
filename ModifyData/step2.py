"""
通过笔记搜索达人
"""

import pandas as pd
import os

def extract_daren(folder_path):
    # 读取文件
    sample_path = os.path.join(folder_path, 'merged_excel.xlsx')
    excel_file = pd.ExcelFile(sample_path)

    # 获取指定工作表中的数据
    df = excel_file.parse('Sheet1')

    # 提取主页链接列的数据
    url_data = df[['主页链接']]
    res_df = url_data.drop_duplicates()

    # 将提取的数据保存为新的 Excel 文件
    sample_path = os.path.join(folder_path, 'daren_urls.xlsx')
    if not os.path.exists(sample_path):
        os.system(r"touch {}".format(sample_path))  # 调用系统命令行来创建文件
    res_df.to_excel(sample_path, index=False)



if __name__ == "__main__":
    # extract_daren("../Tiktok/shipin")
    extract_daren("../xhs/biji")
