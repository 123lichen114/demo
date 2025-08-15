import json
from use_llm.My_LLM import ask_LLMmodel
from datetime import datetime, timedelta
from Handle_csv.Util import calculate_time_diff
import pandas as pd
import numpy as np
from Util import *
from use_GaoDe_api.geo import *
from Handle_csv.scenario.navigation.basic_info import *
from Handle_csv.config import Config

# map={
#     "基础信息":{"城市":"","居住地":"","工作地":""},
#     "时间规律":{"出行周期偏好":"","出行时段偏好":"","高峰出行模式":""},
#     "空间范围":{"单次出行距离":"","活动区域":""},
#     "目的地偏好":{"高频目的地类型":""},
#     "通勤基础":{"规律性行程":"","规律行程距离":"","规律行程耗时":""},
#     "通勤空间":{"通勤方向":""},
#     "工作习惯":{"工作时长":""}
# }
class Basic_feature_label:
    def __init__(self,navi_info:navi_info,config:Config) -> None:
        # self.home_name = self.set_home_name(poi_info_list)
        self.navi_info = navi_info
        poi_info_list = navi_info.Get_json_info()['poi_info_list']
        self.home_name = navi_info.home
        # self.workplace = self.set_work_location(poi_info_list)
        self.workplace = navi_info.workplace
        
        self.basic_features_labels_mapping = self.get_features_labels_mapping(poi_info_list)
        
        pass
    
    def show_basic_feature_label(self) -> pd.DataFrame:
        tuples_list = []
        value_list = []
        for feature, labels in self.basic_features_labels_mapping.items():
            for label in labels:
                tuples_list.append((feature, label))
                value_list.append(self.basic_features_labels_mapping[feature][label])
        # 创建多级列索引
        multi_columns = pd.MultiIndex.from_tuples(
            tuples_list,
            names=['feature', 'label']
        )
        df = pd.DataFrame([value_list],columns=multi_columns)
        return df

    def get_features_labels_mapping(self,
                                    poi_info_list,
                                    template_json="Handle_csv/scenario/navigation/basic_features_labels_mapping_template.json"):
        basic_features_labels_mapping = {}
        with open(template_json, 'r') as f:
            basic_features_labels_mapping = json.load(f)

        for feature,labels in basic_features_labels_mapping.items():
            if feature == "通勤基础":
                # ret_info = self.sub_classify_6(poi_info_list)
                ret_info = self.sub_classify_6(poi_info_list)
                # print(basic_features_labels_mapping[feature])
                # print(type(basic_features_labels_mapping[feature]))
                for label in labels:
                    value = ret_info[label]
                    basic_features_labels_mapping[feature][label] = ret_info[label]
                continue
            for label in labels:
                basic_features_labels_mapping[feature][label] = self.classify((feature,label),poi_info_list)
                
        return basic_features_labels_mapping

    
    def classify(self,feature_label_tuple,poi_info_list):
        if feature_label_tuple == ("基础信息","居住地") :
            return self.home_name
        elif feature_label_tuple == ("基础信息","工作地") :
            return self.workplace

        elif feature_label_tuple == ("时间规律","出行周期偏好") :
            return self.sub_classify_1(poi_info_list)
        elif feature_label_tuple == ("时间规律","出行时段偏好") :
            return self.sub_classify_2(poi_info_list)
        elif feature_label_tuple == ("空间范围","单次出行距离") :
            return self.sub_classify_3(poi_info_list)
        
        elif feature_label_tuple == ("空间范围","活动区域") :
            return self.sub_classify_4(poi_info_list)
        
        elif feature_label_tuple == ("目的地偏好","高频目的地类型") :
            return self.sub_classify_5(poi_info_list)
        
        elif feature_label_tuple == ("通勤空间","通勤方向") :
            return self.sub_classify_9(poi_info_list)
        elif feature_label_tuple == ("工作习惯","工作时长") :
            return self.sub_classify_11(poi_info_list)
        elif feature_label_tuple == ("时间规律","高峰出行模式") :
            return self.sub_classify_12(poi_info_list)
        else:
            return ""
        
    
    def sub_classify_1(self,poi_info_list) -> str:
        # ("时间规律","出行周期偏好")
        week_day = []
        for info in poi_info_list:
            week_day.append(is_weekday(info['start_time']))
        if len(week_day) == 0:
            return "缺少信息，无法判断"
        # 计算 工作日出行率
        workday_rate = week_day.count(True) / len(week_day)
        if workday_rate > 0.8:
            return "工作日主导型"
        elif workday_rate <0.4:
            return "周末主导型"
        else:
            return "均衡型"
        
    
    def sub_classify_2(self,poi_info_list) -> str:
        # （"时间规律","出行时段偏好")
        # 用util中get_hour统计每个时间段出现的次数 poi_info_dict的格式为 [{poi: "xxx", type: "xxx", start_time: "xxx", end_time: "xxx"}]
        time_interval = []
        for poi_item in poi_info_list:
            time_interval.append(get_hour(poi_item['start_time']))
        if time_interval == []:
            return "缺少信息，无法判断"
        #对time_interval中的元素进行计数，统计7-18,>18，<7出现的次数
        count_7_18 = time_interval.count("7-18")
        count_19later = time_interval.count(">18")
        count_7earlier = time_interval.count("<7")
        #如果7-18的次数大于80%，则返回"白天主导型"
        if count_7_18 / len(time_interval) > 0.5:
            return "日间活跃型"
        elif count_19later / len(time_interval) > 0.5:
            return "夜间活跃型"
        elif count_7earlier / len(time_interval) > 0.5:
            return "凌晨活跃型"
        else:
            return "均衡型"

        

    def sub_classify_3(self,poi_info_list) -> str:
        # ("空间范围","单次出行距离")
        # 计算所有出行距离的平均值
        total_distance = []
        # 将poi_info_dict中的每一项按照天划分，用get_date函数
        days = {}
        for poi_item in poi_info_list:
            date = get_date(poi_item['start_time'])
            if date not in days:
                days[date] = []
            days[date].append(poi_item)
        

        # 每一天去第一个地点默认从家出发，立刻当天最后一个地点默认回家，计算每一段行程的距离，并累加到total_distance中计算所有出行距离的平均值
        
        for day in days:
            for i in range(len(days[day])):
                if i == 0:
                    total_distance.append(get_driving_path_distance_by_loc(days[day][i]['start_location'],days[day][i]['poi_location']))
                elif i == len(days[day])-1:
                    total_distance.append(get_driving_path_distance_by_loc(days[day][i]['start_location'],days[day][i]['poi_location']))
                else:
                    total_distance.append(get_driving_path_distance_by_loc(days[day][i]['start_location'],days[day][i]['poi_location']))
        if len(total_distance) == 0:
            return "缺少信息，无法判断"
        # 统计total_distance，小于5000的比例大于70%，则返回"短途主导型"，超过50%在5000-200000之间，则返回"中途主导型"，超过40%在20000以上，则返回"长途主导型"，其他情况返回"均衡复合型"
        #小于5000的比例
        count_5000 = len([i for i in total_distance if i < 5000]) / len(total_distance)
        count_5000_20000 = len([i for i in total_distance if i >= 5000 and i <= 20000]) / len(total_distance)
        count_20000 = len([i for i in total_distance if i > 20000]) / len(total_distance)
        if count_5000 > 0.7:
            return "短途主导型"
        elif count_5000_20000 > 0.5:
            return "中途主导型"
        elif count_20000 > 0.4:
            return "长途主导型"
        else:
            return "均衡复合型"

        
    def sub_classify_4(self, poi_info_list) -> str:
    # ("空间范围","出行范围")
        def get_str_value(value):
            """处理可能为列表的值，提取字符串（如果是列表则取第一个元素）"""
            if isinstance(value, list):
                # 如果是列表，返回第一个元素（假设列表非空且第一个元素是字符串）
                return value[0] if value else ""
            else:
                # 否则直接返回（假设是字符串或None）
                return value if value is not None else ""
    
        area_spans: list[dict]
        area_spans = self.navi_info.get_area_span()
        city_district = {}
        
        for area_span in area_spans:
            target_area = area_span['end_administrative_division']
            
            # 处理city和district，确保是字符串类型
            city = get_str_value(target_area.get('city'))
            district = get_str_value(target_area.get('district'))
            
            # 使用处理后的城市和区县作为键
            key = (city, district)
            
            if key not in city_district:
                city_district[key] = 1
            else:
                city_district[key] += 1
        
        # 统计每个（市，区）出现的次数，如果出现跨市的行程，则返回”跨城活动“，
        # 如果90%以上目的地在同一个区，则返回”单区域活动“,
        # 否则返回”多区域活动“
        cities = []
        for city, district in city_district:
            if city not in cities:
                cities.append(city)
        
        # 处理没有数据的特殊情况
        if not city_district:
            return "未知活动范围"  # 或者根据业务需求返回其他默认值
        
        if len(cities) > 1:
            return "跨城活动"
        elif max(city_district.values()) / sum(city_district.values()) > 0.9:
            return "单区域活动"
        else:
            return "多区域活动"

    def sub_classify_5(self,poi_info_list) -> str:
        # ("目的地偏好","高频目的地类型")
        # 统计每个地点类型出现的次数 poi_info_dict的格式为 [{poi: "xxx", type: "xxx", start_time: "xxx", end_time: "xxx"}]
        activity_types = {}
        for poi_item in poi_info_list:
            if poi_item['poi'] != self.home_name and poi_item['poi'] != self.workplace:
                if poi_item['type'] in activity_types:
                    activity_types[poi_item['type']] += 1
                else:
                    activity_types[poi_item['type']] = 1
        if activity_types == {}:
            return "无出行记录"
        # 把activity_types这个字典按value大小排序，输出[(key, value), (key, value), ...]
        high_frequency_activity_types = sorted(activity_types.items(), key=lambda x: x[1], reverse=True)
        #返回最高频地点类型
        return high_frequency_activity_types[0][0]

    
    def sub_classify_6(self,poi_info_list):
        # ("通勤基础","规律性行程")
        # input = poi_info_list
        # prompt = f"请根据输入的用户出行信息{poi_info_list}，判断用户是否具有规律性行程，分以下几种情况： \
        #             1.至少一对“在相似时间、往返于相似地点”的重复行程。 则直接回复：两点通勤者 \
        #             2.有固定的居住地，但工作地点不唯一，经常在多个固定的办公区或客户地点之间移动。 则直接回复：多点通勤者 \
        #             3.未发现满足以上两种条件的情况。 则直接回复：无规律性行程 "
        # return ask_LLMmodel(input,prompt)

        """
        分析POI信息列表，判断用户是否有规律性行程
        
        参数:
            poi_info_list: POI信息列表，每个元素包含
                {
                'start_location':self.start_location,
                'poi':self.poi_name,
                'type':self.poi_type,
                'poi_location':self.poi_location,
                'start_time':self.start_time,
                '':self.end_time
            }end_time
        返回:
            包含行程规律信息的字典
        """
        if len(poi_info_list) == 0:
            return {
                "规律性行程":"无导航出行记录，无法判断",
                "规律行程距离": "无",
                "规律行程耗时": "无"
            }
        # 转换为DataFrame便于处理
        df = pd.DataFrame(poi_info_list)
        
        # 解析时间
        df['start_datetime'] = df['start_time'].apply(parse_datetime)
        df['end_datetime'] = df['end_time'].apply(parse_datetime)
        df['date'] = df['start_datetime'].apply(lambda x: x.date())
        
        # 存储地点对及其对应的时间段
        location_pairs = defaultdict(list)
        
        # 提取所有可能的地点对（按时间顺序）
        for i in range(len(df)):
            for j in range(i+1, len(df)):
                # 确保是不同天的行程
                if df.loc[i, 'date']!= df.loc[j, 'date']:
                    # 确定地点对（按字母顺序排序确保A-B和B-A被视为同一对）
                    loc1 = df.loc[i, 'poi']
                    loc2 = df.loc[j, 'poi']
                    sorted_loc = tuple(sorted([loc1, loc2]))
                    
                    # 记录两个行程的时间段
                    location_pairs[sorted_loc].append({
                        'start': df.loc[i, 'start_datetime'],
                        'end': df.loc[i, 'end_datetime']
                    })
                    location_pairs[sorted_loc].append({
                        'start': df.loc[j, 'start_datetime'],
                        'end': df.loc[j, 'end_datetime']
                    })
        
        # 判断是否有符合条件的地点对（相似时间段）
        result_pairs = []
        # 定义时间差阈值（30分钟），可根据需要调整
        TIME_THRESHOLD = timedelta(minutes=30)
        
        for pair, time_ranges in location_pairs.items():
            # 需要至少两对不同天的行程
            if len(time_ranges) >= 2:
                # 检查时间段是否相似
                # 计算平均开始时间和结束时间
                start_times = [tr['start'] for tr in time_ranges]
                end_times = [tr['end'] for tr in time_ranges]
                
                # 计算平均开始时间（转换为时间戳计算）
                avg_start_ts = sum(dt.timestamp() for dt in start_times) / len(start_times)
                avg_start = datetime.fromtimestamp(avg_start_ts)
                
                # 计算平均结束时间
                avg_end_ts = sum(dt.timestamp() for dt in end_times) / len(end_times)
                avg_end = datetime.fromtimestamp(avg_end_ts)
                
                # 检查所有时间是否在平均时间的阈值范围内
                all_similar = True
                for tr in time_ranges:
                    if (abs(tr['start'] - avg_start) > TIME_THRESHOLD or 
                        abs(tr['end'] - avg_end) > TIME_THRESHOLD):
                        all_similar = False
                        break
                
                if all_similar:
                    # 格式化平均时间段
                    avg_time_str = f"{avg_start.strftime('%H:%M:%S')}-{avg_end.strftime('%H:%M:%S')}"
                    result_pairs.append((pair[0], pair[1], avg_time_str))
        
        if result_pairs:
            #计算规律行程的平均距离，用get_driving_path_distance_by_address计算
            avg_distance = 0
            for pair in result_pairs:
                avg_distance += get_driving_path_distance_by_address(self.city,pair[0], pair[1])
            avg_distance /= len(result_pairs)
            #计算规律行程的平均时间，用calculate_time_diff计算
            avg_time = 0
            for pair in result_pairs:
                avg_time += calculate_time_diff(pair[2].split('-')[0],pair[2].split('-')[1],time_format="%H:%M:%S")/3600
            avg_time /= len(result_pairs)
            ret_info = {
                "规律性行程":f"两点通勤者:{result_pairs}",
                "规律行程距离":f"{avg_distance}米",
                "规律行程耗时":f"{avg_time}分钟"
            }
            return ret_info
        else:
            ret_info ={
                "规律性行程":"无规律性行程",
                "规律行程距离": "无",
                "规律行程耗时": "无"
            }
            return ret_info
        

    def sub_classify_7(self,poi_info_list) -> str:
        # ("通勤基础","通勤时长")
        return "待实现"

    def sub_classify_8(self,poi_info_list) -> str:
        return "待实现"

    def sub_classify_9(self,poi_info_list) -> str:
        return "待实现"
    
    def sub_classify_11(self,poi_info_list) -> str:
        # ("工作习惯","工作时长")
        if self.workplace == "无法确认用户工作地点":
            return "无法确认用户工作地点"
        scaned_work_location = False
        work_start_time = None
        work_time_list = []
        for poi_item in poi_info_list:
            if scaned_work_location and work_start_time != None and poi_item['poi'] != self.workplace:
                work_time_list.append(calculate_time_diff(work_start_time,poi_item['end_time'])/3600)
                #保留2位小数
                scaned_work_location = False
            if poi_item['poi'] == self.workplace:
                scaned_work_location = True
                work_start_time = poi_item['end_time']
        if  len(work_time_list) > 0:
            work_time = sum(work_time_list)/len(work_time_list)
            if work_time < 6:
                return "灵活/短时"
            elif work_time >10 :
                return "超长工时"
            else:
                return "标准工时"
        return "work_time_list is []"
    
    def sub_classify_12(self,poi_info_list) -> str:
        # ("时间规律","高峰出行模式")
        # 用util中get_hour统计每个时间段出现的次数 poi_info_dict的格式为 [{poi: "xxx", type: "xxx", start_time: "xxx", end_time: "xxx"}]
        time_interval = []
        for poi_item in poi_info_list:
            start_hour = get_hour(poi_item['start_time'])
            if (start_hour>=7 and start_hour<=9) or (start_hour>=17 and start_hour<=19):
                time_interval.append("高峰")
            else:
                time_interval.append("非高峰")
        if time_interval == []:
            return "无法确认"   
        #对time_interval中的元素进行计数，统计高峰和非高峰出现的次数
        count_peak = time_interval.count("高峰")
        count_non_peak = time_interval.count("非高峰")
        #如果高峰出现的次数大于非高峰出现的次数，则返回"高峰出行型"
        if count_peak/len(time_interval) > 0.7:
            return "高峰期出行者"
        else:
            return "错峰出行者"
        