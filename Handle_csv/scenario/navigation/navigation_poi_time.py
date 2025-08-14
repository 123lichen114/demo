import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from io import BytesIO
from Handle_csv.Util import parse_datetime
from use_GaoDe_api.geo import get_location_geo
from use_GaoDe_api.draw import draw_ordered_points
from use_llm.My_LLM import ask_LLMmodel
from collections import defaultdict
import os
# 核心函数：绘制用户路线时序图（纵轴时间段视觉增强）
def plot_route_timeline(json_data):
    """
    优化纵轴显示，使时间段在视觉上更长更清晰
    只在右上角显示地点对应的颜色块图例
    """
    plt.rcParams["font.family"] = ["Heiti TC", "Arial Unicode MS"]
    plt.rcParams["axes.unicode_minus"] = False
    
    
    # 提取地点和时间数据
    locations = []
    start_datetimes = []
    end_datetimes = []

    for entry in json_data:
        if "poi" in entry and "start_time" in entry and "end_time" in entry:
            try:
                start_dt = parse_datetime(entry["start_time"])
                end_dt = parse_datetime(entry["end_time"])
                
                if end_dt > start_dt:
                    start_datetimes.append(start_dt)
                    end_datetimes.append(end_dt)
                    location = entry["poi"].strip()
                    locations.append(location)
                else:
                    print(f"跳过无效时间数据: {entry}，结束时间应晚于开始时间")
                    
            except Exception as e:
                print(f"跳过无效数据: {entry}，错误: {str(e)}")

    if not start_datetimes:
        print("未找到有效数据，请检查JSON格式是否包含'poi'、'start_time'和'end_time'字段")
        return None
    
    # 关键调整：大幅增加纵向尺寸，使纵轴视觉上更长
    fig, ax = plt.subplots(figsize=(10, 15))  # 宽度10，高度18，纵向空间显著增加
    fig.patch.set_facecolor('#f0f2f6')  # 匹配Streamlit背景
    
    # 处理日期（x轴）
    all_dates = [dt.date() for dt in start_datetimes] + [dt.date() for dt in end_datetimes]
    dates = sorted(list(set(all_dates)))
    date_indices = {date: i for i, date in enumerate(dates)}
    
    # 处理时间段（y轴，保持2小时一段但增加视觉高度）
    time_slots = [f"{i:02d}:00-{i+2:02d}:00" for i in range(0, 24, 2)]
    
    # 为地点分配唯一颜色和位置偏移
    unique_locations = list(set(locations))
    color_list = list(mcolors.TABLEAU_COLORS.values()) + list(mcolors.CSS4_COLORS.values())
    color_map = {loc: color_list[i % len(color_list)] for i, loc in enumerate(unique_locations)}
    location_offset = {loc: (i % 5) * 0.15 - 0.3 for i, loc in enumerate(unique_locations)}
    
    # 绘制数据：线段表示停留时间，散点表示开始和结束点
    for start_dt, end_dt, loc in zip(start_datetimes, end_datetimes, locations):
        # 计算坐标
        start_x = date_indices[start_dt.date()]
        start_y = start_dt.hour / 2 + location_offset[loc]
        end_x = date_indices[end_dt.date()]
        end_y = end_dt.hour / 2 + location_offset[loc]
        
        # 绘制线段表示停留时间段
        ax.plot(
            [start_x, end_x], [start_y, end_y],
            color=color_map[loc],
            linewidth=5,
            alpha=0.7,
            zorder=2
        )
        
        # 绘制开始时间点（圆形）
        ax.scatter(
            start_x, start_y,
            color=color_map[loc],
            s=200,  # 增大点尺寸
            alpha=0.9,
            edgecolors='black',
            linewidth=1.5,
            marker='o',
            zorder=3
        )
        
        # 绘制结束时间点（方形）
        ax.scatter(
            end_x, end_y,
            color=color_map[loc],
            s=200,  # 增大点尺寸
            alpha=0.9,
            edgecolors='black',
            linewidth=1.5,
            marker='s',
            zorder=3
        )
        
        # 添加停留时长标签
        duration = (end_dt - start_dt).total_seconds() / 3600
        if duration > 1:
            mid_x = (start_x + end_x) / 2
            mid_y = (start_y + end_y) / 2
            ax.text(
                mid_x, mid_y,
                f"{duration:.1f}h",
                fontsize=11,
                ha='center',
                va='center',
                bbox=dict(facecolor='white', alpha=0.8, pad=3, boxstyle='round,pad=0.3')
            )
    
    # 配置坐标轴 - 重点优化纵轴显示
    ax.set_xticks(range(len(dates)))
    ax.set_xticklabels(
        [date.strftime("%Y-%m-%d") for date in dates],
        rotation=45,
        ha='right',
        fontsize=11
    )
    
    # 增加纵轴范围，使时间段间隔更大
    ax.set_ylim(-0.8, 11.8)
    ax.set_yticks(range(len(time_slots)))
    ax.set_yticklabels(time_slots, fontsize=12)  # 增大纵轴标签字体
    ax.invert_yaxis()
    
    # 增加纵轴刻度线密度，增强纵向视觉引导
    ax.yaxis.set_major_locator(plt.MultipleLocator(1))
    ax.yaxis.set_minor_locator(plt.MultipleLocator(0.5))
    ax.grid(True, which='major', linestyle='--', alpha=0.8, linewidth=1.2)
    ax.grid(True, which='minor', linestyle=':', alpha=0.5, linewidth=0.8)
    
    # 添加标题和标签
    ax.set_title("用户路线时序分布（含停留时间）", fontsize=18, pad=20)
    ax.set_xlabel("日期", fontsize=14, labelpad=10)
    ax.set_ylabel("时间段", fontsize=14, labelpad=20)  # 增加纵轴标签间距
    
    # 创建地点颜色块图例（右上角）
    legend_elements = [
        plt.Line2D([0], [0], color=color_map[loc], lw=8, label=loc)
        for loc in unique_locations
    ]
    
    ax.legend(
        handles=legend_elements,
        title="地点",
        bbox_to_anchor=(1.05, 1.0),
        loc='upper left',
        fontsize=11,
        title_fontsize=13,
        frameon=True
    )
    
    # 调整布局，为纵轴留出更多空间
    plt.subplots_adjust(right=0.8, left=0.15)  # 增加左侧边距，确保纵轴标签完整显示
    plt.tight_layout()
    
    # 保存到缓冲区
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    buf.seek(0)
    return buf
        
    


def plot_route(json_data):
    print("json_data = ",json_data)
    poi_location_list = [item['poi_location'] for item in json_data]
    locations =[]
    for location in poi_location_list:
        location = [float(i) for i in location.split(',')]
        locations.append(location)
    print("locations = ",locations)
    # 返回路线图
    return draw_ordered_points(locations, key='6617df78ec04efcba67789cc7e02895b', save_path=None)

def plot_route_by_date(json_data, save_dir=None):
    """
    按日期划分导航数据，并为每个日期绘制路线图
    
    参数:
        json_data: 导航数据列表（即nav_data）
        save_dir: 可选，保存图片的目录路径
        
    返回:
        字典，键为日期字符串，值为对应日期的地图二进制数据或None（失败时）
    """
    print("开始按日期处理导航数据...")
    
    # 1. 按日期分组
    date_groups = defaultdict(list)
    for item in json_data:
        # 提取日期部分（假设start_time格式为"YYYY-MM-DD HH:MM:SS"或类似）
        try:
            start_time = item['start_time']
            date_str = start_time.split(' ')[0]  # 分割出日期部分
            date_groups[date_str].append(item)
        except (KeyError, IndexError) as e:
            print(f"处理数据项时出错：{str(e)}，跳过该数据项")
            continue
    
    if not date_groups:
        print("错误：没有有效的数据可处理")
        return {}
    
    print(f"成功按日期分组，共{len(date_groups)}天数据")
    
    # 2. 为每个日期绘制路线图
    results = {}
    key = '6617df78ec04efcba67789cc7e02895b'  # API密钥
    
    for date_str, items in date_groups.items():
        print(f"\n处理{date_str}的数据...")
        
        # 提取该日期的所有poi_location
        try:
            poi_location_list = [item['poi_location'] for item in items]
            locations = []
            for location in poi_location_list:
                # 将"经度,纬度"字符串转换为[float, float]
                lon, lat = location.split(',')
                locations.append([float(lon), float(lat)])
            
            print(f"{date_str}共有{len(locations)}个地点")
            
            # 生成保存路径（如果指定了保存目录）
            save_path = None
            if save_dir:
                os.makedirs(save_dir, exist_ok=True)
                save_path = os.path.join(save_dir, f"route_{date_str}.png")
            
            # 调用绘图函数
            map_data = draw_ordered_points(
                locations=locations,
                key=key,
                save_path=save_path
            )
            
            results[date_str] = map_data
            
            if map_data:
                print(f"{date_str}的路线图生成成功")
            else:
                print(f"{date_str}的路线图生成失败")
                
        except Exception as e:
            print(f"处理{date_str}时出错：{str(e)}")
            results[date_str] = None
    
    return results

# 使用示例
if __name__ == "__main__":
    # 示例导航数据
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
    ]
    
    # 调用按日期绘制路线图的函数
    # 可指定save_dir参数保存图片，如save_dir="route_maps"
    results = plot_route_by_date(sample_data)
    
    # 输出结果信息
    for date, data in results.items():
        status = "成功" if data else "失败"
        print(f"{date}的路线图生成{status}")