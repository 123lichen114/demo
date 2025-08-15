import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Any

# 设置中文字体
plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["font.family"] = ["Heiti TC"]
plt.rcParams["axes.unicode_minus"] = False

def plot_destination_time_heatmap(nav_data: List[Dict[str, Any]]) -> None:
    """
    绘制目的地与时间段相关性热力图
    
    参数:
        nav_data: 导航数据列表，包含目的地和时间信息
    """
    if not nav_data:
        raise ValueError("导航数据为空，无法绘制热力图")  # 检查输入数据是否为空
        
    # 转换数据格式，将列表形式的导航数据转换为DataFrame格式
    df = pd.DataFrame(nav_data)
    
    # 提取日期和小时信息
    if 'start_time' not in df.columns:
        raise KeyError("导航数据缺少'start_time'字段")
        
    # 确保时间列是datetime类型
    df['start_time'] = pd.to_datetime(df['start_time'], errors='coerce')
    df = df.dropna(subset=['start_time'])
    
    # 提取小时和目的地名称
    df['hour'] = df['start_time'].dt.hour
    df['poi'] = df.get('poi', df.get('poi_name', '未知'))
    
    # 统计每个目的地在每个小时的出现次数
    heatmap_data = df.groupby(['poi', 'hour']).size().unstack(fill_value=0)
    
    # 创建热力图
    plt.figure(figsize=(12, 8))
    sns.heatmap(heatmap_data, cmap="YlOrRd", annot=True, fmt="d", cbar_kws={'label': '出现次数'})
    plt.title('目的地与时间段相关性热力图', fontsize=15)
    plt.xlabel('时间段（小时）', fontsize=12)
    plt.ylabel('目的地', fontsize=12)
    plt.tight_layout()
    

def plot_destination_type_pie(nav_data: List[Dict[str, Any]]) -> None:
    """
    绘制目的地类型饼状图
    
    参数:
        nav_data: 导航数据列表，包含目的地类型信息
    """
    if not nav_data:
        raise ValueError("导航数据为空，无法绘制饼状图")
        
    # 转换数据格式
    df = pd.DataFrame(nav_data)
    
    # 提取目的地类型
    type_column = 'type'
    
    # 统计各类型数量
    type_counts = df[type_column].value_counts()
    
    # 合并占比过小的类型
    threshold = 0.03  # 3%阈值
    type_counts = type_counts / type_counts.sum()
    small_types = type_counts[type_counts < threshold].sum()
    type_counts = type_counts[type_counts >= threshold]
    if small_types > 0:
        type_counts['其他'] = small_types
    
    # 创建饼状图
    plt.figure(figsize=(10, 8))
    wedges, texts, autotexts = plt.pie(
        type_counts, 
        labels=type_counts.index,
        autopct='%1.1f%%',
        startangle=140,
        wedgeprops=dict(width=0.4)  # 环形图效果
    )
    
    # 美化文本
    plt.setp(texts, size=12)
    plt.setp(autotexts, size=10, color="black", weight="bold")
    plt.title('目的地类型分布', fontsize=15)
    plt.tight_layout()

if __name__ == "__main__":
    # 示例数据
    nav_data = [
        {"start_time": "2023-10-01 08:00:00", "poi": "公司", "type": "工作"},
        {"start_time": "2023-10-01 09:00:00", "poi": "餐厅", "type": "餐饮"},
        {"start_time": "2023-10-01 10:00:00", "poi": "公司", "type": "工作"},
        {"start_time": "2023-10-01 11:00:00", "poi": "咖啡厅", "type": "休闲"},
        {"start_time": "2023-10-01 12:00:00", "poi": "餐厅", "type": "餐饮"},
        {"start_time": "2023-10-01 13:00:00", "poi": "公司", "type": "工作"}]

    plot_destination_time_heatmap(nav_data)
    plt.show()
    plot_destination_type_pie(nav_data)
    plt.show()
