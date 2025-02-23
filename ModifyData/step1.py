import pandas as pd
import os

def merge_and_sample(folder_path):
    """合并数据并抽取100条样本"""
    # 获取文件夹中所有数据文件
    data_files = [
        f for f in os.listdir(folder_path)
        if f.endswith(('.xlsx', '.xls', '.csv'))
    ]

    if not data_files:
        print(f"{folder_path} 中没有找到数据文件")
        return

    # 读取并合并数据
    all_data = []
    for file in data_files:
        file_path = os.path.join(folder_path, file)
        try:
            if file.endswith('.csv'):
                df = pd.read_csv(file_path, encoding="utf-8", engine='python')
            else:
                df = pd.read_excel(file_path)
            all_data.append(df)
        except Exception as e:
            print(f"读取文件 {file} 失败：{str(e)}")

    if not all_data:
        print(f"{folder_path} 没有成功读取任何文件")
        return

    # 合并并去重
    merged_df = pd.concat(all_data, ignore_index=True).drop_duplicates()
    
    # 保存完整合并文件
    merged_path = os.path.join(folder_path, 'merged_excel.xlsx')
    if not os.path.exists(merged_path):
        os.system(r"touch {}".format(merged_path))  # 调用系统命令行来创建文件
    merged_df.to_excel(merged_path, index=False)


    # 抽取特征样本（修正版）
    sample_size = min(100, len(merged_df))
    if sample_size == 0:
        print(f"{folder_path} 合并后为空文件，跳过采样")
        return

    # 第一阶段：分层抽样
    grouped = merged_df.groupby(merged_df.columns[0], group_keys=False)
    stage1_sample = grouped.apply(lambda x: x.sample(min(2, len(x))))

    # 判断是否需要补充抽样
    current_num = len(stage1_sample)
    need_num = sample_size - current_num

    if need_num > 0:
        # 第二阶段：补充随机抽样
        stage2_sample = merged_df.sample(
            n=need_num,
            replace=len(merged_df) < need_num,
            random_state=42
        )
        sampled_df = pd.concat([stage1_sample, stage2_sample]) \
            .sample(frac=1, random_state=42) \
            .head(sample_size)
    else:
        sampled_df = stage1_sample.sample(n=sample_size, random_state=42)

    # 保存样本文件
    sample_path = os.path.join(folder_path, 'sample_100.xlsx')
    if not os.path.exists(sample_path):
        os.system(r"touch {}".format(sample_path))  # 调用系统命令行来创建文件
    sampled_df.to_excel(sample_path, index=False)


if __name__ == "__main__":
    paths = [
        "../xhs/biji",
        "../xhs/daren", 
        "../Tiktok/shipin",
        "../Tiktok/zhanghao"
    ]
    
    for path in paths:
        merge_and_sample(path)
        print(f"{'='*30}\n{path} 处理完成\n{'='*30}")




