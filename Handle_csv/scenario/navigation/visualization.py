import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

def analyze_navigation_data(nav_data):
    """
    分析导航数据，生成目的地与时间段相关性热力图和目的地类型饼状图
    
    参数:
        nav_data: 包含导航信息的列表，每个元素是一个字典
    """
    # print("lc code")
    # 设置中文显示
    plt.rcParams["font.family"] = ["Heiti TC"]
    plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题
    
    # 转换为DataFrame并预处理
    df = pd.DataFrame(nav_data)
    
    # 检查必要的列是否存在
    required_columns = ['poi', 'type', 'start_time']
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"导航数据缺少必要的字段: {col}")
    
    # 处理时间数据
    try:
        df['start_time'] = pd.to_datetime(df['start_time'])
    except Exception as e:
        raise ValueError(f"时间格式转换错误: {str(e)}")
    
    # 生成两种分析图表
    plot_destination_time_correlation(df)
    plot_destination_type_pie(df)
    
    return df

def plot_destination_time_correlation(df):
    """绘制目的地与导航时间段的相关性热力图"""
    # 定义时间段划分函数
    def get_time_period(hour):
        if 0 <= hour < 6:
            return '凌晨（0-5）'
        elif 6 <= hour < 9:
            return '早高峰（6-8）'
        elif 9 <= hour < 12:
            return '上午（9-11）'
        elif 12 <= hour < 14:
            return '午休（12-13）'
        elif 14 <= hour < 18:
            return '下午（14-17）'
        elif 18 <= hour < 21:
            return '晚高峰（18-20）'
        else:
            return '夜间（21-23）'
    
    # 提取小时并划分时间段
    df['hour'] = df['start_time'].dt.hour
    df['time_period'] = df['hour'].apply(get_time_period)
    
    # 按时间顺序排序时间段
    period_order = [
        '凌晨（0-5）', '早高峰（6-8）', '上午（9-11）',
        '午休（12-13）', '下午（14-17）', '晚高峰（18-20）', '夜间（21-23）'
    ]
    df['time_period'] = pd.Categorical(df['time_period'], categories=period_order, ordered=True)
    
    # 计算交叉表
    corr_table = pd.crosstab(
        index=df['poi'],
        columns=df['time_period'],
        values=df['start_time'],
        aggfunc='count'
    ).fillna(0)
    
    # 绘制热力图
    plt.figure(figsize=(12, 8))
    sns.heatmap(
        corr_table,
        annot=True,
        fmt='.0f',
        cmap='YlOrRd',
        cbar_kws={'label': '导航次数'}
    )
    
    plt.title('目的地与导航时间段的相关性热力图', fontsize=15)
    plt.xlabel('导航时间段', fontsize=12)
    plt.ylabel('目的地', fontsize=12)
    plt.tight_layout()
    plt.show()
    
    return corr_table

def plot_destination_type_pie(df, threshold=0.05):
    """优化后的饼状图：显示数量、百分比和总数"""
    # 统计各类型数量
    type_counts = df['type'].value_counts()
    total = type_counts.sum()  # 计算总导航次数
    
    # 合并低频类型为“其他”
    if total > 0:
        others = type_counts[type_counts / total < threshold].sum()
        if others > 0:
            type_counts = type_counts[type_counts / total >= threshold]
            type_counts['其他'] = others
    
    # 绘制饼图
    plt.figure(figsize=(10, 8))
    
    # 自定义标签：包含类型名称和数量（例如“住宅区: 20次”）
    labels = [f'{label}: {count}次' for label, count in zip(type_counts.index, type_counts)]
    
    # 绘制饼图，autopct显示百分比
    wedges, texts, autotexts = plt.pie(
        type_counts,
        labels=labels,  # 使用带数量的标签
        autopct='%1.1f%%',  # 显示百分比
        startangle=90,
        wedgeprops={'edgecolor': 'white', 'linewidth': 1},
        textprops={'fontsize': 11}  # 标签字体大小
    )
    
    # 美化百分比标签
    plt.setp(autotexts, size=10, color='black', weight='bold')
    
    # 标题显示总导航次数
    plt.title(f'导航目的地类型分布（总次数：{total}次）', fontsize=15)
    
    plt.axis('equal')  # 保证圆形
    plt.tight_layout()
    plt.show()
    
    return type_counts  # 返回各类型数量统计

# 使用示例
if __name__ == "__main__":
    # 示例数据
    sample_data = [
        {'start_location': '121.370007,31.192397',
         'poi': '金地西郊风华',
         'type': '住宅区',
         'poi_location': '121.434522,31.2165',
         'start_time': '2025-06-20 22:43:23.708',
         'end_time': '2025-06-20 23:24:45.718'},
        {'start_location': '121.380007,31.182397',
         'poi': '万达广场',
         'type': '商业区',
         'poi_location': '121.424522,31.2065',
         'start_time': '2025-06-20 19:43:23.708',
         'end_time': '2025-06-20 20:10:45.718'},
        {'start_location': '121.390007,31.172397',
         'poi': '金地西郊风华',
         'type': '住宅区',
         'poi_location': '121.434522,31.2165',
         'start_time': '2025-06-21 07:15:23.708',
         'end_time': '2025-06-21 07:45:45.718'},
        {'start_location': '121.400007,31.162397',
         'poi': '人民公园',
         'type': '休闲区',
         'poi_location': '121.414522,31.1965',
         'start_time': '2025-06-21 15:30:23.708',
         'end_time': '2025-06-21 16:00:45.718'},
    ]
    
    # 调用分析函数
    result_df = analyze_navigation_data(sample_data)
    print("数据分析完成！")
