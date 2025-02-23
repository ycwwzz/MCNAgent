import os

import pandas as pd
import re
import numpy as np

# 读取数据
df = pd.read_excel("../xhs/daren/merged_excel.xlsx")

# 定义目标城市和行业CPM均值
TARGET_CITY = "广州"
INDUSTRY_CPM_MEAN = 800

# 数据预处理
df.replace("--", pd.NA, inplace=True)
numeric_cols = ["粉丝数", "图文CPM", "视频CPM"]
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")


# 一票否决项筛选
def filter_city(row):
    city_check = TARGET_CITY in row["地域"] if pd.notna(row["地域"]) else False
    match = re.search(r"广东(\d+\.\d+)%", str(row["粉丝地域"]))
    percent = float(match.group(1)) if match else 0
    return city_check and (percent >= 60)


qualified_mask = df.apply(filter_city, axis=1)
qualified = df[qualified_mask]


# 评分模型计算
def calculate_scores(sub_df):
    scores = []
    for _, row in sub_df.iterrows():
        try:
            # 互动率得分
            fans = int(row["粉丝数"]) if pd.notna(row["粉丝数"]) else 0
            avg_like = int(row["近60天平均点赞"]) if pd.notna(row["近60天平均点赞"]) else 0
            avg_collect = int(row["近60天平均收藏"]) if pd.notna(row["近60天平均收藏"]) else 0

            collect_rate = (avg_collect / fans * 100) if fans > 0 else 0
            like_rate = (avg_like / fans * 100) if fans > 0 else 0
            interaction_score = (collect_rate * 0.5 + like_rate * 0.3 + 8 * 0.2) / 15 * 30

            # 粉丝地域得分
            match = re.search(r"广东(\d+\.\d+)%", str(row["粉丝地域"]))
            city_percent = float(match.group(1)) if match else 0
            city_score = 25 - max(0, (80 - city_percent) // 5 * 5)

            # 爆款率得分（假设20%）
            viral_score = 16

            # CPM得分
            cpm = min(row["图文CPM"] if pd.notna(row["图文CPM"]) else 1000,
                      row["视频CPM"] if pd.notna(row["视频CPM"]) else 1000)
            cpm_diff = (cpm - INDUSTRY_CPM_MEAN) // (INDUSTRY_CPM_MEAN * 0.1)
            cpm_score = 15 - max(0, cpm_diff) * 3

            # 关键词得分
            keywords = ["人均", "打卡", "套餐"]
            tags = str(row["达人标签"]).lower()
            desc = str(row["简介"]).lower()
            matches = sum(1 for kw in keywords if kw in tags or kw in desc)
            keyword_score = min(10, matches * 3)

            total = sum([interaction_score, city_score, viral_score, cpm_score, keyword_score])
            scores.append(round(total, 1))
        except Exception as e:
            print(f"计算错误：{str(e)}")
            scores.append(0)
    return scores


# 计算并添加评分
df["总分"] = np.nan
df.loc[qualified.index, "总分"] = calculate_scores(qualified)

# 新增步骤：删除未得分的行（保留总分非空的行）
df = df.dropna(subset=['总分'])



folder_path = "../xhs/daren"
output_file_path = "result_with_scores.xlsx"
output_file = os.path.join(folder_path, output_file_path)
if not os.path.exists(output_file):
    os.system(r"touch {}".format(output_file))  # 调用系统命令行来创建文件
# 保存结果到新文件
df.to_excel(output_file, index=False)

print("文件已保存为'sample_filtered_scores.xlsx'，仅保留有效评分数据。")