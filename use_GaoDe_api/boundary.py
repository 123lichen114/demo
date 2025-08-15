import requests
import json
import geopandas as gpd
import matplotlib.pyplot as plt
import folium
from shapely.geometry import Polygon, MultiPolygon
from shapely.errors import WKTReadingError
import numpy as np
from geopy.distance import geodesic  # 计算球面距离
def visualize_boundary(keywords: str, interactive: bool = False, save_path=None):
    """
    可视化指定地区的边界
    参数:
        keywords: 地区名称
        interactive: 是否生成交互式地图
        save_path: 保存图片路径，为None则不保存
    """
    # 获取边界数据
    boundary_str = get_boundary_from_api(keywords)
    if not boundary_str:
        print("无法获取边界数据，可视化失败")
        return
    
    # 解析边界数据
    try:
        polygons = []
        # 分割多个多边形（如果有）
        for poly_str in boundary_str.split('|'):
            # 分割点坐标
            points = poly_str.split(';')
            # 转换为(经度, 纬度)元组列表
            coords = [tuple(map(float, point.split(','))) for point in points if point]
            # 创建多边形
            if len(coords) >= 3:  # 多边形至少需要3个点
                polygons.append(Polygon(coords))
        
        if not polygons:
            print("无法解析有效的边界数据")
            return
            
        # 创建MultiPolygon
        multi_poly = MultiPolygon(polygons)
        
        # 创建GeoDataFrame
        gdf = gpd.GeoDataFrame(
            {'name': [keywords], 'geometry': [multi_poly]},
            crs="EPSG:4326"  # WGS84坐标系
        )
        
    except (ValueError, WKTReadingError) as e:
        print(f"解析边界数据出错: {e}")
        return
    
    # 静态可视化
    if not interactive:
        fig, ax = plt.subplots(figsize=(12, 10))
        # 设置中文字体
        plt.rcParams["font.family"] = ["Heiti TC"]
        
        # 绘制边界
        gdf.plot(ax=ax, edgecolor='darkblue', facecolor='lightblue', alpha=0.6, linewidth=2)
        
        # 添加标题和标签
        ax.set_title(f'{keywords} 行政区划边界', fontsize=16)
        ax.set_xlabel('经度', fontsize=12)
        ax.set_ylabel('纬度', fontsize=12)
        
        # 美化图表
        ax.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        # 保存图片
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"图片已保存至: {save_path}")
        
        plt.show()
    
    # 交互式可视化
    else:
        # 计算中心点
        centroid = multi_poly.centroid
        center = [centroid.y, centroid.x]  # folium使用[纬度, 经度]
        
        # 创建地图
        m = folium.Map(location=center, zoom_start=10, tiles='CartoDB positron')
        
        # 添加边界
        folium.GeoJson(
            gdf,
            style_function=lambda x: {
                'fillColor': '#3186cc',
                'color': '#1e5b94',
                'weight': 2,
                'fillOpacity': 0.3
            },
            tooltip=folium.GeoJsonTooltip(fields=['name'], aliases=[f'{keywords}'])
        ).add_to(m)
        
        # 添加标记点
        folium.Marker(
            location=center,
            popup=keywords,
            icon=folium.Icon(color='blue', icon='map-marker')
        ).add_to(m)
        
        # 保存为HTML
        if save_path:
            m.save(save_path)
            print(f"交互式地图已保存至: {save_path}")
        else:
            # 在Jupyter环境中显示
            return m

# 复用边界获取函数（优化错误处理）
def get_boundary_from_api(keywords: str) -> str:
    """获取地区边界坐标字符串（polyline格式）"""
    key = '6617df78ec04efcba67789cc7e02895b'  # 替换为有效key
    url = r'https://restapi.amap.com/v3/config/district'
    params = {
        "key": key,
        "keywords": keywords,
        "extensions": 'all'
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        res = response.json()
        if res.get("status") != "1":
            print(f"API错误: {res.get('info')}")
            return ""
        return res["districts"][0]["polyline"]
    except (requests.exceptions.RequestException, KeyError, IndexError) as e:
        print(f"获取边界失败: {e}")
        return ""

# 计算地区几何中心（质心）
def get_geometric_center(boundary_str: str) -> tuple[float, float]:
    """
    从边界坐标计算地区的几何中心（纬度, 经度）
    处理多多边形情况（如包含飞地），返回整体质心
    """
    if not boundary_str:
        return (0.0, 0.0)
    
    all_points = []
    # 解析多多边形边界
    for poly_str in boundary_str.split('|'):
        points = [p.split(',') for p in poly_str.split(';') if p]
        # 转换为(经度, 纬度)浮点数
        coords = [(float(lng), float(lat)) for lng, lat in points]
        all_points.extend(coords)
    
    if not all_points:
        return (0.0, 0.0)
    
    # 计算所有点的平均坐标（近似质心）
    lngs = [p[0] for p in all_points]
    lats = [p[1] for p in all_points]
    center_lng = np.mean(lngs)
    center_lat = np.mean(lats)
    return (center_lat, center_lng)  # (纬度, 经度)

# 比较两个点的几何中心性
def compare_geometric_centrality(
    keywords: str,
    point1: tuple[float, float],  # (纬度, 经度)
    point2: tuple[float, float]   # (纬度, 经度)
) -> dict:
    """
    比较两个点在目标地区内的几何中心性
    返回距离几何中心的距离及中心性判断
    """
    # 1. 获取地区边界
    boundary_str = get_boundary_from_api(keywords)
    if not boundary_str:
        return {"error": "无法获取地区边界"}
    
    # 2. 计算地区几何中心
    center = get_geometric_center(boundary_str)
    if center == (0.0, 0.0):
        return {"error": "无法计算几何中心"}
    
    # 3. 计算两点到几何中心的球面距离（单位：千米）
    dist1 = geodesic(point1, center).kilometers
    dist2 = geodesic(point2, center).kilometers
    
    # 4. 判断中心性
    result = {
        "地区": keywords,
        "几何中心": (round(center[0], 6), round(center[1], 6)),
        "点1坐标": point1,
        "点1到中心距离(km)": round(dist1, 3),
        "点2坐标": point2,
        "点2到中心距离(km)": round(dist2, 3),
        "中心性判断": "点1更高" if dist1 < dist2 else "点2更高"
    }
    return result

# 示例用法
if __name__ == "__main__":
    # 静态可视化示例
    # visualize_boundary("北京市", interactive=False)
    
    # #交互式可视化示例（会生成HTML文件）
    # visualize_boundary("上海市", interactive=True, save_path="use_GaoDe_api/shanghai_boundary.html")
    
    # #可视化其他地区
    # visualize_boundary("广东省")
    # visualize_boundary("深圳市")
    beijing_point1 = (39.915, 116.404)  # 王府井
    beijing_point2 = (39.997, 116.337)  # 回龙观
    result = compare_geometric_centrality("北京市", beijing_point1, beijing_point2)
    print(result)
    boundary = get_boundary_from_api('上海市')
    #把boundary写入json文件
    with open('use_GaoDe_api/boundary.json','w',encoding='utf-8') as f:
        f.write(json.dumps(boundary,ensure_ascii=False,indent=2))