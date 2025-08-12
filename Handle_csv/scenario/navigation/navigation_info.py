import pandas as pd
import json

from Util import find_any_key,extract_json_from_string,calculate_time_diff
from Handle_csv.scenario.scenario_util import get_scenario_info
from use_llm.My_LLM import ask_LLMmodel
from Handle_csv.scenario.navigation.basic_info import *
def classify_poi_type(poi_list) -> dict:
    prompt = f"""
    你是一个专业的地点类型分类器。请根据以下POI信息进行分类：
    POI信息：{poi_list}
    请返回一个字典，键值都是双引号字符串
    键: POI名称（poi_list中的一项)
    值: POI类型（如餐厅、商店、景点等）。
    如果两个poi属于同一类，那么它们在字典中对应的值应该一样。
    """
    response = ask_LLMmodel(poi_list, prompt)
    try:
        output_json = extract_json_from_string(response)
        return output_json
    except json.JSONDecodeError:
        print(f"无法解析LLM响应: {response}")
        return {"poi": poi_list, "type": "未知"}

def navigation_related(row) -> bool:
    # 判断行是否与导航相关
    if row['app_source'] is not None:
        if 'onemap' in row['app_source']:
            return True
    if row['voice_dc'] is not None:
        # 尝试将 voice_dc 字符串转换为列表（包含若干字典）
        try:
            dc = eval(row['voice_dc'])
            for d in dc:
                if d['domain'] == 'navigation' or d['command'] == 'global/navigation':
                    return True
        except:
            print("voice_dc is not a valid list of dictionaries.")
    return False

def get_navigation_related_row(df):
    return get_scenario_info(df, navigation_related)

def get_location(row):
    json_dict = json.loads(row['status_json'])
    for d in json_dict:
        if d["name"] == "Vehicle.Travel.OneMap.Navi.DestinationPosition":
            location = d["value"]
            if location:
                location = json.loads(location)
                location_str = f"{location['longitude']},{location['latitude']}"
                return location_str
    return None
def extract_poi_from_navigation_related_row(navigation_related_row):
    
    # 提取POI信息
    poi_info = []
    poi_list = []
    last_place_location = None
    for index, row in navigation_related_row.iterrows():
        json_dict = json.loads(row['json_all'])
        poi_keyword_list = ['poi_name', 'poi']
        poi = find_any_key(json_dict, poi_keyword_list)
        if poi is not None and row["event_key"] == 'X_Map_008_0002':
            start_time = row['format_time_ms']
            # description = row['desc']
            end_time = "不确定"
            location_str = get_location(row)
            if location_str is None:
                continue
            #从这一行的下一行开始往下历遍行，找到下一个event_key为X_Map_009_0006的行
            for next_index in range(index+1, len(navigation_related_row)):
                next_row = navigation_related_row.loc[next_index]
                if next_row["event_key"] == 'X_Map_009_0006':
                    end_time = next_row['format_time_ms']
                    break
            if end_time == "不确定": # 如果没有找到结束时间，则跳过
                continue
            poi_list.append(poi)
            poi_info.append({
                "poi": poi,
                "poi_location": location_str,
                "start_time": start_time,
                "end_time": end_time
            })
    # 对poi_info进行精简，如果同一天内，有连续的几项poi相同，则合并它们的时间范围
    def merge_poi_info(poi_info):
        merged_info = []
        for i in range(len(poi_info)):
            if i == 0:
                merged_info.append(poi_info[i])
            else:
                time_threold = 1200  # 20分钟
                if poi_info[i]['poi'] == merged_info[-1]['poi'] and calculate_time_diff(poi_info[i]['start_time'], merged_info[-1]['start_time']) < time_threold:
                    merged_info[-1]['start_time'] = poi_info[i]['start_time']
                    merged_info[-1]['end_time'] = poi_info[i]['end_time']
                else:
                    merged_info.append(poi_info[i])
        return merged_info
    poi_info = merge_poi_info(poi_info)
    def add_start_location(poi_list):
        """
        为poi列表中的每个字典添加start_location字段
        - 第一个元素的start_location为所有poi_location的平均坐标
        - 后续元素的start_location为上一个元素的poi_location
        
        参数:
            poi_list: 包含poi信息的列表，每个元素需有'poi_location'字段（格式如'116.407,39.904'）
        
        返回:
            处理后的新列表（原列表不会被修改）
        """
        # 避免修改原列表，创建副本进行处理
        processed_list = [item.copy() for item in poi_list]
        total = len(processed_list)
        
        if total == 0:
            return processed_list  # 空列表直接返回
        
        # 提取所有经纬度并转换为浮点数
        lng_list = []
        lat_list = []
        for item in processed_list:
            lng_str, lat_str = item["poi_location"].split(',')
            lng_list.append(float(lng_str))
            lat_list.append(float(lat_str))
        
        # 计算平均坐标（保留6位小数，与原始格式一致）
        avg_lng = sum(lng_list) / total
        avg_lat = sum(lat_list) / total
        avg_loc = f"{avg_lng:.6f},{avg_lat:.6f}"
        
        # 为第一个元素设置平均坐标作为start_location
        processed_list[0]["start_location"] = avg_loc
        
        # 为后续元素设置上一个元素的poi_location作为start_location
        for i in range(1, total):
            processed_list[i]["start_location"] = processed_list[i-1]["poi_location"]
        
        return processed_list

    poi_info = add_start_location(poi_info)
    poi_type_dict = classify_poi_type(poi_list)
    for poi_item in poi_info:
        poi_item["type"] = poi_type_dict[poi_item["poi"]]
    return poi_info

def get_navigation_info(df,config = None)->navi_info:
    # 获取导航信息
    navigation_related_row = get_navigation_related_row(df)
    # 提取POI信息
    poi_info_list = extract_poi_from_navigation_related_row(navigation_related_row)
    Navi_info = navi_info([poi_info(info_dict) for info_dict in poi_info_list],config=config)
    return Navi_info


if __name__ == "__main__":
    # 示例调用
    csv_folder = '../data/sequences'  # 替换为实际的 CSV 文件路径
    df = pd.read_csv('/Users/lichen18/Documents/Project/Data_mining/data/all_sequence_HLX14B178R0001811_merged.csv')
    print('navigation_related_row:', get_navigation_info(df))