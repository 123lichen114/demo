import json
import re
import pandas as pd
# 新增：导入绘图所需库
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime,timedelta
from matplotlib.dates import DateFormatter, DayLocator
import matplotlib.colors as mcolors
from io import BytesIO
from collections import defaultdict

def read_json_as_string(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)  # 解析 JSON 为 Python 对象
        return json.dumps(data, ensure_ascii=False)  # 转换为字符串



def extract_json_from_string(json_string):
    """
    从字符串中提取 JSON 数据并保存到文件
    
    参数:
    json_string (str): 包含 JSON 数据的字符串
    output_file (str, optional): 输出文件路径。默认为 None。
    indent (int, optional): JSON 缩进空格数。默认为 2。
    返回:
    dict: 解析后的 JSON 数据
    """
    try:
        # 尝试直接解析字符串
        data = json.loads(json_string)
    except json.JSONDecodeError:
        # 如果直接解析失败，尝试提取字符串中的 JSON 部分
        # 使用正则表达式匹配大括号包含的内容
        json_match = re.search(r'\{.*\}', json_string, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            try:
                data = json.loads(json_str)
            except json.JSONDecodeError as e:
                raise ValueError(f"无法解析 JSON: {str(e)}")
        else:
            raise ValueError("在字符串中未找到有效的 JSON 格式数据")
    
    return data


# 核心函数：解析时间格式（适配2025-06-29 00:33:23.569 这种时间格式）
def parse_datetime(time_str):
    """解析带毫秒的时间字符串"""
    try:
        return datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S.%f")
    except ValueError:
        try:
            # 兼容不带毫秒的格式
            return datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            raise ValueError(f"无法解析时间格式: {time_str}")

def find_any_key(nested_obj, target_keys):
    """
    从嵌套字典/列表中查找目标键列表中任意一个键的值（找到第一个匹配的就返回）
    
    参数：
        nested_obj: 嵌套的字典或列表（JSON转换的对象）
        target_keys: 目标键的列表（如 ["key1", "key2"]）
    
    返回：
        第一个匹配到的键的值；若所有键都未找到，返回 None
    """
    # 确保目标键列表是可迭代的（处理输入为单个字符串的情况）
    if isinstance(target_keys, str):
        target_keys = [target_keys]
    
    # 1. 处理字典：检查当前层是否包含目标键列表中的任何一个键
    if isinstance(nested_obj, dict):
        # 遍历目标键列表，检查是否有键存在于当前字典中
        for key in target_keys:
            if key in nested_obj and nested_obj[key]!= "":
                return nested_obj[key]  # 找到第一个匹配的键，返回其值
        # 若当前层无匹配，递归处理所有值（深入嵌套结构）
        for value in nested_obj.values():
            result = find_any_key(value, target_keys)
            if result is not None:  # 子层级找到匹配，立即返回
                return result
    
    # 2. 处理列表：遍历列表中的每个元素，递归查找
    elif isinstance(nested_obj, list):
        for item in nested_obj:
            result = find_any_key(item, target_keys)
            if result is not None:  # 列表元素中找到匹配，立即返回
                return result
    
    # 3. 非字典/列表类型：无键可查，返回 None
    return None

def get_scenario_info(df,scenario_related_func)  -> pd.DataFrame:
    df = df.replace(np.nan, None)
    all_scenario_info = pd.DataFrame(columns=df.columns)
    # 遍历DataFrame的每一行
    # 如果这一行与scenario相关，则将其加入到all_scenario_info表中
    # 遍历DataFrame的每一行
    for index,row in df.iterrows():
        if scenario_related_func(row):
            # 把这一行加入到 all_scenario_info表中，concat方法
            row_df = row.to_frame().T
            all_scenario_info = pd.concat([all_scenario_info, row_df], ignore_index=True)
    return all_scenario_info

def calculate_time_diff(format_start_time, format_end_time ,time_format = "%Y-%m-%d %H:%M:%S.%f"):
    start_time = datetime.strptime(format_start_time, time_format)
    end_time = datetime.strptime(format_end_time, time_format)
    return (end_time - start_time).total_seconds()

#判断某一天是周几
def get_weekday(format_date_str):
    date_format = "%Y-%m-%d %H:%M:%S.%f"
    date = datetime.strptime(format_date_str, date_format)
    return date.weekday()

#判断某个时间是否属于工作日
def is_weekday(format_date_str):
    weekday = get_weekday(format_date_str)
    return weekday < 5

#判断一个时间处于一天中的几时
def get_hour(format_date_str):
    date_format = "%Y-%m-%d %H:%M:%S.%f"
    date = datetime.strptime(format_date_str, date_format)
    return date.hour

#提取日期
def get_date(format_date_str):
    date_format = "%Y-%m-%d %H:%M:%S.%f"
    date = datetime.strptime(format_date_str, date_format)
    return date.date()