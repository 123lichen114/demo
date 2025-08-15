import folium
from folium import PolyLine, CircleMarker
from folium.plugins import MarkerCluster, MiniMap
from datetime import datetime
from typing import List, Dict, Any

def create_daily_navigation_maps(poi_info_list: List[Dict[str, Any]]) -> List[folium.Map]:
    """
    根据导航数据创建按天分组的交互式地图
    
    参数:
        poi_info_list: 导航POI信息列表
        
    返回:
        按天分组的交互式地图列表
    """
    # 按日期分组数据
    daily_data = {}
    
    for item in poi_info_list:
        # 提取日期部分（去除时间）
        try:
            date_str = datetime.strptime(item['start_time'], "%Y-%m-%d %H:%M:%S.%f").date()
        except (KeyError, ValueError):
            # 处理日期格式错误
            continue
            
        if date_str not in daily_data:
            daily_data[date_str] = []
        daily_data[date_str].append(item)
    
    # 为每一天创建地图
    maps = []
    for date, data in sorted(daily_data.items()):
        # 创建地图，以第一条数据的起点为中心
        try:
            first_start = data[0]['start_location'].split(',')
            center_lat, center_lon = float(first_start[1]), float(first_start[0])
        except (IndexError, ValueError):
            # 如果无法获取起点，使用默认位置（上海）
            center_lat, center_lon = 31.2304, 121.4737
        
        # 创建地图实例
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=13,
            tiles='CartoDB Positron'  # 浅色地图样式，适合展示路线
        )
        
        # 添加小地图插件
        MiniMap().add_to(m)
        
        # 添加标记聚类
        marker_cluster = MarkerCluster().add_to(m)
        
        # 存储所有点用于自动调整视野
        all_points = []
        
        # 添加起点标记
        start_loc = data[0]['start_location'].split(',')
        try:
            start_lon, start_lat = float(start_loc[0]), float(start_loc[1])
            CircleMarker(
                location=[start_lat, start_lon],
                radius=10,
                color='green',
                fill=True,
                fill_color='green',
                fill_opacity=0.7,
                popup=f"起点: {datetime.strptime(data[0]['start_time'], '%Y-%m-%d %H:%M:%S.%f').strftime('%H:%M')}"
            ).add_to(marker_cluster)
            all_points.append([start_lat, start_lon])
        except (IndexError, ValueError):
            pass
        
        # 存储路线点用于绘制路线
        route_points = []
        if all_points:
            route_points.append(all_points[0])
        
        # 添加每个POI的标记
        for i, item in enumerate(data):
            try:
                # 解析POI位置
                poi_loc = item['poi_location'].split(',')
                poi_lon, poi_lat = float(poi_loc[0]), float(poi_loc[1])
                
                # 添加POI标记
                CircleMarker(
                    location=[poi_lat, poi_lon],
                    radius=8,
                    color='blue' if i < len(data)-1 else 'red',
                    fill=True,
                    fill_color='blue' if i < len(data)-1 else 'red',
                    fill_opacity=0.7,
                    popup=f"""
                    <strong>{item['poi']}</strong><br>
                    类型: {item['type']}<br>
                    到达: {datetime.strptime(item['end_time'], '%Y-%m-%d %H:%M:%S.%f').strftime('%H:%M')}
                    """
                ).add_to(marker_cluster)
                
                all_points.append([poi_lat, poi_lon])
                route_points.append([poi_lat, poi_lon])
                
            except (IndexError, ValueError, KeyError):
                continue
        
        # 绘制路线
        if len(route_points) > 1:
            PolyLine(
                route_points,
                color='orange',
                weight=4,
                opacity=0.7,
                dash_array='5, 10'
            ).add_to(m)
        
        # 添加标题
        folium.map.Marker(
            [center_lat, center_lon],
            icon=folium.DivIcon(
                html=f"""<div style="font-weight: bold; font-size: 16px;">
                        导航路线 - {date.strftime('%Y年%m月%d日')}
                       </div>""",
                icon_size=(300, 30)
            )
        ).add_to(m)
        
        # 调整地图视野以显示所有点
        if all_points:
            m.fit_bounds(all_points)
        
        maps.append(m)
    
    return maps

if __name__ == '__main__':
    pass