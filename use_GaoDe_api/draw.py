import requests
import os
import json
def draw_ordered_points(locations, key, size="800*600", 
                        scale=1,
                        line_color="0x0000FF", 
                        line_weight=5,
                        marker_color="0xFF0000", label_color="0xFFFFFF",
                        label_bg_color="0x5288d8", 
                        save_path=None):
    """
    绘制按顺序连接的经纬度点，使用labels字段为地点编号（支持任意序号）
    
    参数:
        locations: 二维列表，每个元素为[经度, 纬度]
        key: 高德地图Web服务API密钥
        size: 地图尺寸，格式"宽度*高度"，默认"800*600"
        scale: 清晰度（1=普通，2=高清），默认1
        line_color: 折线颜色（十六进制），默认0x0000FF（蓝色）
        line_weight: 折线粗细（2-15），默认5
        marker_color: 标注点颜色，默认0xFF0000（红色）
        label_color: 标签文字颜色（十六进制），默认0xFFFFFF（白色）
        label_bg_color: 标签背景色（十六进制），默认0x5288d8（蓝色）
        save_path: 可选，图片保存路径（如不需要保存可设为None）
    
    返回:
        成功：地图图片的二进制数据（response.content）
        失败：None
    """
    # 1. 基础校验
    if not key:
        print("错误：请传入有效的高德API密钥（key）")
        return None
    
    if len(locations) < 2:
        print("错误：至少需要2个点才能绘制连线")
        return None
    
    for i, loc in enumerate(locations):
        if len(loc) != 2:
            print(f"错误：第{i+1}个点格式错误，需为[经度, 纬度]（如[116.3, 39.9]）")
            return None
        try:
            lon = float(loc[0])
            lat = float(loc[1])
            if not (-180 <= lon <= 180 and -90 <= lat <= 90):
                print(f"错误：第{i+1}个点经纬度超出范围（经度[-180,180]，纬度[-90,90]）")
                return None
        except ValueError:
            print(f"错误：第{i+1}个点经纬度必须为数字，当前值：{loc}")
            return None
    
    # 2. 构建API参数
    ## 2.1 折线参数（按顺序连接所有点）
    points_str = ";".join([f"{lon},{lat}" for lon, lat in locations])
    paths_param = f"{line_weight},{line_color},1,0x0000FF,0.5:{points_str}"  # 透明度1（不透明）
    
    ## 2.2 标注点参数（仅显示标记，无内置label）
    marker_size = "small"
    markers_param = f"{marker_size},{marker_color},0:{';'.join([f'{lon},{lat}' for lon, lat in locations])}"
    
    ## 2.3 标签参数（使用labels字段实现编号，支持任意序号）
    labels_list = []
    for i, (lon, lat) in enumerate(locations, 1):
        # 构建label_style字符串（注意逗号分隔，无多余符号）
        label_style = (
            f"地点{i},"       # content：序号（支持10以上数字）
            "0,"          # font：0=微软雅黑
            "1,"          # bold：1=粗体
            "12,"         # fontSize：12号字
            f"{label_color},"  # fontColor：文字颜色
            f"{label_bg_color}"  # background：背景色
        )
        # 拼接单个标签：样式:经纬度
        single_label = f"{label_style}:{lon},{lat}"
        labels_list.append(single_label)
    
    # 多个标签用分号分隔
    labels_param = "|".join(labels_list)
    
    # 3. 发送请求
    api_url = "https://restapi.amap.com/v3/staticmap"
    params = {
        "key": key,
        "paths": paths_param,
        "markers": markers_param,  # 标注点样式
        "labels": labels_param,    # 标签样式及位置
        "size": size,
        "scale": scale
    }
    with open("use_GaoDe_api/params.json", "w") as f:
        json.dump(params,f, indent=2,ensure_ascii=False)
    try:
        print("正在请求高德API...")
        response = requests.get(api_url, params=params, timeout=15)
        
        # 4. 校验响应是否为图片
        if "image" not in response.headers.get("Content-Type", ""):
            print(f"API返回错误：{response.text}")
            return None
        
        # 5. 可选：保存图片
        if save_path:
            save_dir = os.path.dirname(save_path)
            if save_dir and not os.path.exists(save_dir):
                os.makedirs(save_dir)
            
            if os.path.exists(save_path):
                os.remove(save_path)
            
            with open(save_path, "wb") as f:
                f.write(response.content)
            
            if os.path.getsize(save_path) < 1024:
                print("错误：生成的图片为空或损坏")
                os.remove(save_path)
                return None
            
            print(f"成功：地图已保存至 {os.path.abspath(save_path)}")
        
        # 6. 返回图片二进制数据
        return response.content
    
    except requests.exceptions.ConnectTimeout:
        print("错误：连接超时，请检查网络")
        return None
    except requests.exceptions.ReadTimeout:
        print("错误：读取超时，API响应过慢")
        return None
    except requests.exceptions.RequestException as e:
        print(f"请求异常：{str(e)}")
        return None


# 使用示例
if __name__ == "__main__":
    # 示例经纬度（包含10个点，测试序号超过9的场景）
    route_points = [
        [116.39748, 39.90882],   # 1
        [116.403874, 39.914885], # 2
        [115.410000, 39.520000], # 3
        [117.410000, 39.120000], # 4
        [113.410000, 39.020000], # 5
        [116.000000, 39.200000], # 9
        [115.000000, 39.100000], # 10（超过原marker label的9限制）
    ]
    
    AMAP_KEY = "6617df78ec04efcba67789cc7e02895b"  # 替换为实际密钥
    
    # 调用函数
    map_data = draw_ordered_points(
        locations=route_points,
        key=AMAP_KEY,
        line_color="0x008000",  # 绿色折线
        marker_color="0xFF5733", # 橙色标注点
        label_color="0x000000",  # 黑色文字
        label_bg_color="0xFFFF00", # 黄色背景
        save_path="use_GaoDe_api/route_map_with_labels.png"
    )
    
    if map_data:
        print(f"成功获取地图数据，大小：{len(map_data)}字节")