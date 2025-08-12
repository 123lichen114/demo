import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from io import BytesIO
from Util import parse_datetime
from use_GaoDe_api.geo import get_location_geo
from use_GaoDe_api.draw import draw_ordered_points
from use_llm.My_LLM import ask_LLMmodel
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