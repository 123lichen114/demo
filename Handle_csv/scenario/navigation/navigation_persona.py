import json
from use_llm.My_LLM import ask_LLMmodel
from datetime import datetime
from Handle_csv.Util import calculate_time_diff
import pandas as pd
import numpy as np
from Handle_csv.scenario.navigation.navigation_feature_label_new import Basic_feature_label
class Navi_Persona:
    def __init__(self,poi_info,config=None) -> None:
        # 1. 核心锚点与通勤模式 （家和公司）
        # 这是用户画像中最基础、最稳定的空间特征，如同骨架。通常通过分析用户长时间停留的地点来识别。
        self.home_location = self.set_home_location(poi_info)
        self.work_location = self.set_work_location(poi_info)
        self.commuting_distance = 0
        self.commuting_time = self.get_commuting_time(poi_info)
        self.commuting_direction = ""
        
        # 2. 活动范围与空间足迹 （结合地图可视化的方式）
        # 这描述了用户生活的“边界”和空间的“形状”，反映了其生活延展性和探索性。
        self.activity_radius = 0
        self.new_location_discovery_rate = self.get_new_location_discovery_rate(poi_info)
        self.footprint_area = 0
        self.footprint_shape = ""
        self.spatial_concentration = ""
        
        #活动类型与场所偏好
        #这揭示了用户的兴趣、消费习惯和生活方式，是画像的“血肉”。这通常通过分析用户停留点的POI（Point of Interest）类型来获得

        self.high_frequency_activity_types = self.get_high_frequency_activity_types(poi_info)
        self.activity_time_preference = ""
        self.brand_preferernce = self.get_brand_preferernce(poi_info)
        self.public_space_preference = self.get_public_space_preference(poi_info)
        self.consumption_level_preference = ""

        #移动规律与行为模式 
        # 这描述了用户移动的“节奏”和“习惯”，体现其生活的规律性。
        self.mobility_regularity = ""
        self.peak_travel_time = ""
        self.rout_choice_preference = ""
        self.dwell_time_characteristics = ""


        self.basic_feature_label = Basic_feature_label(poi_info,config).basic_features_labels_mapping
        pass
    
    def show_persona(self):
        json_persona = {
            "居住地-"+"home_location": self.home_location,
            "工作地-"+"work_location": self.work_location,
            "通勤距离-"+"commuting_distance": self.commuting_distance,
            "通勤时间-"+"commuting_time": self.commuting_time,
            "通勤方向-"+"commuting_direction": self.commuting_direction,
            "活动半径-"+"activity_radius": self.activity_radius,
            "新地点探索率-"+"new_location_discovery_rate": self.new_location_discovery_rate,
            "空间足迹面积-"+"footprint_area": self.footprint_area,
            "足迹形态-"+"footprint_shape": self.footprint_shape,
            "空间聚集/离散度-"+"spatial_concentration": self.spatial_concentration,
            "高频活动类型-"+"high_frequency_activity_types": self.high_frequency_activity_types,
            "活动时间偏好-"+"activity_time_preference": self.activity_time_preference,
            "特定品牌偏好-"+"brand_preferernce": self.brand_preferernce,
            "公共/开放空间偏好-"+"public_space_preference": self.public_space_preference,
            "消费层级偏好-"+"consumption_level_preference": self.consumption_level_preference,
            "出行规律性-"+"mobility_regularity": self.mobility_regularity,
            "出行高峰时段-"+"peak_travel_time": self.peak_travel_time,
            "路径选择偏好-"+"rout_choice_preference": self.rout_choice_preference,
            "停留时长特征-"+"dwell_time_characteristics": self.dwell_time_characteristics
        }
        return json.dumps(json_persona, ensure_ascii=False, indent=2)

    # 在下面添加接口函数
    def set_home_location(self,poi_info):
        input = poi_info
        prompt = f"请分析这个列表:{poi_info}，结合其type字段，帮我分析哪个地点（也就是poi字段）是用户的居住地，并直接给出对应的地点名称（列表中其中一项的poi字段值）,如果不能判断出用户的居住地，则直接回答 无法确认用户居住地\n"
        return ask_LLMmodel(input, prompt)
    
    def set_work_location(self,poi_info):
        input = poi_info
        prompt = f"请分析这个列表:{poi_info}，结合其type字段，帮我分析哪个地点（也就是poi字段）是用户的工作或学习的地点，并直接给出对应的地点名称（列表中其中一项的poi字段值）,如果不能判断出用户的居住地，则直接回答 无法确认用户工作地点\n"
        return ask_LLMmodel(input, prompt)

    def get_commuting_time(self,poi_info):
        time_format = "%Y-%m-%d %H:%M:%S.%f"
        poi_info_dict = json.loads(poi_info)
        for poi_item in poi_info_dict:

            if poi_item['poi'] == self.work_location:
                time_diff = calculate_time_diff(poi_item['start_time'],poi_item['end_time'])
                return f"{time_diff / 60:.2f} 分钟"
        return "无法确认通勤时间"

    
    def get_new_location_discovery_rate(self,poi_info):
        # TODO
        
        return 0

    def get_activity_radius(self,poi_info):
        # TODO 在非家-公司地点活动的主要时间段。

        return 0

    def get_footprint_area(self,poi_info):
        # TODO

        return 0

    def get_footprint_shape(self,poi_info):
        # TODO

        return 0

    def get_spatial_concentration(self,poi_info):
        # TODO

        return 0

    def get_high_frequency_activity_types(self,poi_info):
        # TODO
        poi_info_dict = json.loads(poi_info)
        # 统计每个地点类型出现的次数 poi_info_dict的格式为 [{poi: "xxx", type: "xxx", start_time: "xxx", end_time: "xxx"}]
        activity_types = {}
        for poi_item in poi_info_dict:
            if poi_item['poi'] != self.home_location and poi_item['poi'] != self.work_location:
                if poi_item['type'] in activity_types:
                    activity_types[poi_item['type']] += 1
                else:
                    activity_types[poi_item['type']] = 1
        # 把activity_types这个字典按value大小排序，输出[(key, value), (key, value), ...]
        activity_types = sorted(activity_types.items(), key=lambda x: x[1], reverse=True)
        return activity_types

    
    def get_activity_time_preference(self,poi_info):
        # TODO
        

        return 0

    def get_brand_preferernce(self,poi_info):
        # TODO
        input = poi_info
        prompt = f"请分析这个列表:{poi_info}，帮我分析用户对特定连锁品牌（如某咖啡、超市等）的忠诚度。如果能分析出来，则回复：用户是XX（某品牌）的常客。如果无法分析出来，则回复：暂未发现用户的特定品牌偏好。\n"
        return ask_LLMmodel(input,prompt)


    def get_public_space_preference(self,poi_info):
        # TODO
        input = poi_info
        prompt = f"请分析这个列表:{poi_info}，帮我分析用户对公园、广场、滨水区等开放空间的访问频率。如果分析出来用户喜欢去的公共空间，则回复：用户喜欢去一些公共空间，如XX。如果无法分析出来，则回复：暂未发现用户的相关偏好。\n"

        return ask_LLMmodel(input,prompt)


    def get_consumption_level_preference(self,poi_info):
        # TODO

        return 0

    def get_mobility_regularity(self,poi_info):
        # TODO

        return 0

    def get_peak_travel_time(self,poi_info):
        # TODO

        return 0

    def get_rout_choice_preference(self,poi_info):
        # TODO

        return 0

    def get_dwell_time_characteristics(self,poi_info):
        # TODO
        
        return 0

    
    def get_basic_persona(self,poi_info):
        features_labels_mapping ={}
        with open("Handle_csv/scenario/navigation/Basic_persona_template.json") as f:
            features_labels_mapping = json.load(f)
        
        return features_labels_mapping

    def show_basic_feature_label(self) -> pd.DataFrame:
        tuples_list = []
        value_list = []
        for feature, labels in self.basic_feature_label.items():
            for label in labels:
                tuples_list.append((feature, label))
                value_list.append(self.basic_feature_label[feature][label])
        # 创建多级列索引
        multi_columns = pd.MultiIndex.from_tuples(
            tuples_list,
            names=['feature', 'label']
        )
        df = pd.DataFrame([value_list],columns=multi_columns)
        return df