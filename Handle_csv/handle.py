import sys
from pathlib import Path
# 获取 当前目录的绝对路径
dir = str(Path(__file__).parent.resolve())
# 将当前目录添加到系统路径
sys.path.append(dir)
from config import Config
from use_llm.My_LLM import ask_LLMmodel
from Util import *
import pandas as pd
from Handle_csv.scenario.navigation.navigation_info import get_navigation_info
from Handle_csv.scenario.navigation.navigation_poi_time import plot_route_timeline, plot_route
from scenario.navigation.navigation_persona import Navi_Persona
from scenario.navigation.navigation_feature_label_new import Basic_feature_label
from scenario.navigation.basic_info import navi_info
# 自定义函数：分析 DataFrame 基本统计信息
def analyze_dataframe(df):
    """分析 DataFrame 并返回统计信息的 JSON"""
    try:
        # 基本统计信息
        stats = {
            "行数": len(df),
            "列数": len(df.columns),
            "列名": list(df.columns),
            "数据类型": {col: str(df[col].dtype) for col in df.columns},
        }
        return json.dumps(stats, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": f"分析失败: {str(e)}"}, indent=2)

def intention_recognize(df,config):
    prompt = config.get_prompt()
    # df1 = df.drop('desc', axis=1).dropna(axis=1, how='all') 
    selected_columns = ['action_type', 'operate_target', 'input','voice_dc','taskmaster_actionInfo','format_time_ms','event_key']
    df1 = df[selected_columns]
    if df1 is not None:
        # 调用 LLM 模型处理数据
        response = ask_LLMmodel(df1, prompt)
        output_json_info = extract_json_from_string(response)
        output_json_info['vin']['value'] = df.loc[1,'vin']
        
        return json.dumps(output_json_info, ensure_ascii=False, indent=2)
    else:
        return "Error reading the CSV file."

def get_target_info(Navi_info:navi_info, scenario_type):
    config = Navi_info.config
    json_navi_data = Navi_info.Get_json_info()['poi_info_list']
    str_navi_data = str(json_navi_data)
    if scenario_type == 'navigation_json':
        print("Processing navigation scenario...")
        return json_navi_data
    
    elif scenario_type == 'nagivation_draw':
        print("Drawinging navigation scenario...")

        plot_buf = plot_route_timeline(json_navi_data)
        return plot_buf
    
    elif scenario_type == 'route_map':
        print("Drawinging route scenario...")
        fig = plot_route(json_navi_data)
        return fig
    
    elif scenario_type == 'user_overall_profile':
        user_p = Navi_Persona(str_navi_data,config)
        return user_p.show_persona()
    
    elif scenario_type == 'user_basic_feature_label':
        user_basic_feature_label = Basic_feature_label(Navi_info,config)
        return user_basic_feature_label

    else:
        return json.dumps({"error": "Unsupported scenario type."}, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    1














































































































































































































