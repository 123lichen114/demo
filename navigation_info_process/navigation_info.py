
from use_GaoDe_api.geo import *
import pandas as pd
class poi_info:
    def __init__(self,row):
        self.start_location=str(row['start_lon'])+','+str(row['start_lat'])
        self.end_location=str(row['end_lon'])+','+str(row['end_lat'])
        self.create_time=row['create_time']
        #根据经纬度获取具体的地址
        self.start_address=get_location_regeo(self.start_location)
        self.end_address=get_location_regeo(self.end_location)

    def show_json(self):
        print("yes")
        return {
            'start_location':self.start_location,
            'end_location':self.end_location,
            'start_location_name':self.start_address,
            'end_location_name':self.end_address,
            'create_time':self.create_time
        }
def get_poi_info_list(df):
    poi_info_list=[]
    for index,row in df.iterrows():
        poi_info_list.append(poi_info(row).show_json())
    return poi_info_list

def test_navigation_info():
    file_path='/Users/lichen18/Documents/Project/Data_mining/data/new_data/all_sequence_HLX14B172R0001061_withstartloc.csv'
    df=pd.read_csv(file_path)
    print(get_poi_info_list(df))