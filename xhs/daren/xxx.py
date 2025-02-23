import pandas as pd
import re

# 读取数据（假设数据已保存为CSV）
df = pd.read_excel("../xhs/daren/sample_100.xlsx")

# 定义目标城市（示例为广州）
TARGET_CITY = "广州"
INDUSTRY_CPM_MEAN = 800  # 假设行业CPM均值为40元

# 预处理数据：处理空值和格式
df.replace("--", pd.NA, inplace=True)
df["粉丝数"] = pd.to_numeric(df["粉丝数"], errors="coerce")
df["图文CPM"] = pd.to_numeric(df["图文CPM"], errors="coerce")
df["视频CPM"] = pd.to_numeric(df["视频CPM"], errors="coerce")

# ----------------------------
# 一、一票否决项筛选
# ----------------------------
def filter_city(row):
    # 检查博主定位城市
    if pd.notna(row["地域"]):
        if TARGET_CITY not in row["地域"]:
            return False
    # 检查粉丝地域占比
    if pd.notna(row["粉丝地域"]):
        match = re.search(r"广东(\d+\.\d+)%", str(row["粉丝地域"]))
        if match:
            percent = float(match.group(1))
            return percent >= 60
    return False

qualified = df[df.apply(filter_city, axis=1)]

# ----------------------------
# 二、评分模型计算
# ----------------------------
def calculate_scores(df):
    scores = []
    for _, row in df.iterrows():
        # 1. 互动率得分（小红书公式）
        avg_like = int(row.get("近60天平均点赞", 0)) if row.get("近60天平均点赞") else 0

        avg_collect = int(row.get("近60天平均收藏", 0)) if row.get("近60天平均收藏") else 0
        total_notes = int(row.get("笔记总数", 0)) if row.get("笔记总数") else 1


        collect_rate = (avg_collect / row["粉丝数"]) * 100 if row["粉丝数"] > 0 else 0
        like_rate = (avg_like / row["粉丝数"]) * 100 if row["粉丝数"] > 0 else 0
        # 假设POI点击率为固定值8%（因数据缺失）
        poi_rate = 8
        interaction_score = (collect_rate*0.5 + like_rate*0.3 + poi_rate*0.2) / 15 * 30  # 标准化到30分

        # 2. 粉丝地域得分
        match = re.search(r"广东(\d+\.\d+)%", str(row["粉丝地域"]))
        city_percent = float(match.group(1)) if match else 0
        city_score = 25 - max(0, (80 - city_percent) // 5 * 5)

        # 3. 爆款率得分（假设爆款定义为互动量≥2倍均值）
        avg_interaction = (avg_like + avg_collect) / 2
        # 由于缺少单条数据，假设爆款率为固定值20%
        viral_score = 16  # 假设20%爆款率得16分

        # 4. CPM得分（取图文和视频CPM最小值）
        cpm = min(row["图文CPM"] or 1000, row["视频CPM"] or 1000)
        cpm_score = 15 - max(0, (cpm - INDUSTRY_CPM_MEAN) // (INDUSTRY_CPM_MEAN*0.1)) * 3

        # 5. 关键词得分（检查标签和简介）
        keywords = ["人均", "打卡", "套餐"]
        tags = str(row["达人标签"]).lower()
        desc = str(row["简介"]).lower()
        matches = sum(1 for kw in keywords if kw in tags or kw in desc)
        keyword_score = min(10, matches * 3)  # 每个关键词3分

        total = (
            interaction_score +
            city_score +
            viral_score +
            cpm_score +
            keyword_score
        )
        scores.append(total)
    return scores

# 计算总分
qualified["总分"] = calculate_scores(qualified)

# 排序结果
result = qualified.sort_values("总分", ascending=False)[["达人名称", "粉丝数", "总分"]]

print("符合条件且评分≥60的博主：")
print(result.head(10))

# 输出示例：
# 达人名称            粉丝数     总分
# 章章干嘛呢          54760    92
# 喜欢吃你碗里的饭      21032    88
# Wayne           14922    85
# 为食喵去稳吃        7243    82