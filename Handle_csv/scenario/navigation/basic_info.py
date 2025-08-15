from use_GaoDe_api.geo import *
from use_GaoDe_api.district import *
from use_GaoDe_api.draw import *
from Handle_csv.Util import *
from use_llm.My_LLM import ask_LLMmodel
class poi_info: #单次出行的起点和终点信息
    def __init__(self,info_dict: dict)-> None:
        self.start_location = info_dict['start_location'] # '116.407526,39.90403' 经度，纬度
        self.poi = info_dict['poi']
        self.type = info_dict['type']
        self.poi_location = info_dict['poi_location'] # '116.423526,39.91613' 经度，纬度
        self.start_time = info_dict['start_time']
        self.end_time = info_dict['end_time']

    def get_json_info(self):
        json_info = {
            "start_location":self.start_location,
            "poi":self.poi,
            "type":self.type,
            "poi_location":self.poi_location,
            "start_time":self.start_time,
            "end_time":self.end_time
        }
        return json_info
    
    def get_driving_distance(self)->float: #单位米
        return get_driving_path_distance_by_loc(self.start_location,self.poi_location)

    def get_driving_time(self)->float:#单位分钟
        time = calculate_time_diff(self.start_time,self.end_time)/60
        return time
    
    def get_administrative_division(self): #行政区划分
        start_administrative_division = get_district(self.start_location)
        end_administrative_division = get_district(self.poi_location)
        return {
            'start_administrative_division':start_administrative_division,
            'end_administrative_division':end_administrative_division
        }


class navi_info: #一个vin的各段出行信息
    def __init__(self,poi_info_list: list[poi_info],vin ="",config = None) -> None:
        self.poi_info_list = poi_info_list
        self.vin = "待接入"
        self.home = self.get_home_name()
        self.workplace = self.get_workplace_name()
        self.config = config
    


    def Get_json_info(self):
        json_info = {
            'vin':self.vin,
            'home':self.home,
            'poi_info_list': [poi_info.get_json_info() for poi_info in self.poi_info_list]
        }
        return json_info
    
    def get_home_name(self):
        input = self.get_poi_name_list()
        prompt = f"请分析输入的列表{input}，结合其type字段，帮我分析哪个地点（也就是poi字段）是用户的居住地，直接给出对应的地点名称（列表中其中一项的poi字段值）;如果不能判断出用户的居住地，则直接回答 无法确认用户居住地\n"
        return ask_LLMmodel(input,prompt)

    def get_workplace_name(self):
        input = self.get_poi_name_list()
        prompt = f"请分析输入的列表{input}，结合其type字段，帮我分析哪个地点（也就是poi字段）是用户的工作地，直接给出对应的地点名称（列表中其中一项的poi字段值）;如果不能判断出用户的工作地，则直接回答 无法确认用户工作地\n"
        return ask_LLMmodel(input,prompt)

    def get_poi_name_list(self)->list[str]:
        return [poi_info.poi for poi_info in self.poi_info_list]
    
    def get_driving_distance_list(self)->list[float]: 
        return [poi_info.get_driving_distance() for poi_info in self.poi_info_list]

    def get_driving_time_list(self)->list[float]:
        return [poi_info.get_driving_time() for poi_info in self.poi_info_list]
    
    def get_area_span(self)->list[dict]:
        return [poi_info.get_administrative_division() for poi_info in self.poi_info_list]
    
    