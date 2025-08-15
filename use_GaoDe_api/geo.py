import json
import requests
from urllib.parse import quote
from time import sleep
def get_location_geo_json_info(CITY,ADDRESS):
    '''
    (正)地理编码：将详细的结构化地址转换为高德经纬度坐标。且支持对地标性名胜景区、建筑物名称解析为高德经纬度坐标。
    结构化地址举例：北京市朝阳区阜通东大街6号转换后经纬度：116.480881,39.989410
    地标性建筑举例：天安门转换后经纬度：116.397499,39.908722
    '''
    url = 'http://restapi.amap.com/v3/geocode/geo?parameters'
    KEY = '6617df78ec04efcba67789cc7e02895b'
    OUTPUT = 'json'
    params = {
        'city': CITY, #城市名称
        'address': ADDRESS,#详细地址
        'key': KEY,
        'output': OUTPUT
    }
    response = json.loads(requests.get(url, params).content)
    sleep(0.5)
    if 'geocodes' not in response:#如果请求出错
        if response['infocode'] == '30001':
            print(f"请求{CITY},{ADDRESS}出错,地名未识别，现将地名规范化后再次请求")
            return get_location_geo_json_info(CITY,CITY+ADDRESS)
        print(f"请求{CITY},{ADDRESS}的地理编码错误,response:{response}")
        return response

    return response

def get_location_geo(CITY,ADDRESS): #输入是城市和地址，输出是经纬度
    response = get_location_geo_json_info(CITY,ADDRESS)
    # print("response:",response)
    if 'geocodes' not in response:
        print(f"请求{CITY},{ADDRESS}出错")
        print(f"response:{response}")
        return None
    return response['geocodes'][0]['location']

def get_location_regeo_info(LOCATION, OUTPUT='json',RADIUS = 1000,EX = 'all'):
    '''
    逆地理编码：将经纬度转换为详细结构化的地址，且返回附近周边的POI、AOI信息。
    例如：116.480881,39.989410 转换地址描述后：北京市朝阳区阜通东大街6号
    '''
    '''
    逆地理编码：将经纬度转换为详细结构化的地址，且返回附近周边的POI、AOI信息。
    例如：116.480881,39.989410 转换地址描述后：北京市朝阳区阜通东大街6号
    '''
    url = 'https://restapi.amap.com/v3/geocode/regeo'
    KEY = '6617df78ec04efcba67789cc7e02895b'
    params = {
        "location": LOCATION, #经纬度 必填 字符串 如 '116.480881,39.989410'
        "key": KEY, # 开发者申请的API key 必填
        "output": OUTPUT, #返回数据的格式 选填 json或xml
        'radius': RADIUS, #radius 取值范围：0~3000，默认值：1000。单位：米
        'extensions': EX, #返回结果控制，extensions 参数默认取值是 base，也就是返回基本地址信息；extensions 参数取值为 all 时会返回基本地址信息、附近 POI 内容、道路信息以及道路交叉口信息。
        'poitype': '商场|购物服务'# 选填，以下内容需要 extensions 参数为 all 时才生效。逆地理编码在进行坐标解析之后不仅可以返回地址描述，也可以返回经纬度附近符合限定要求的 POI 内容（在 extensions 字段值为 all 时才会返回 POI 内容）。设置 POI 类型参数相当于为上述操作限定要求。参数仅支持传入 POI TYPECODE，可以传入多个 POI TYPECODE，相互之间用“|”分隔。
    }
    response = requests.get(url, params = params)
    # answer = json.loads(response.content)
    # 这种方式也可以
    answer = response.json()
    sleep(0.5)
    return answer

def get_location_regeo(LOCATION):#输入是经纬度，输出是地址
    return get_location_regeo_info(LOCATION,'json','1000','all')['regeocode']['formatted_address']

#驾车路径规划
def get_driving_path_info(ORIGIN,DESTINATION):
    '''
    驾车路径规划：根据起点和终点坐标规划驾车路线，并返回路线规划方案。
    '''
    # 定义请求的URL
    url = 'https://restapi.amap.com/v3/direction/driving'
    # 定义请求的API密钥
    KEY = '6617df78ec04efcba67789cc7e02895b'
    # 定义请求的扩展参数
    EX = 'base'
    # 定义请求的参数
    params = {
        'origin': ORIGIN,
        'destination': DESTINATION,
        'key': KEY,
        'extensions': EX,
    }
    response = requests.get(url, params = params)
    jd = response.json()
    sleep(0.3)
    return jd

def get_driving_path_distance_by_loc(ORIGIN,DESTINATION):#输入是起点终点的经纬度
    jd = get_driving_path_info(ORIGIN,DESTINATION)
    try:
        distance = jd['route']['paths'][0]['distance']
    except Exception as e:
        print(f"计算{ORIGIN}到{DESTINATION}驾车距离出错,response信息：{jd}")
        distance = 0
    return float(distance)

def get_driving_path_distance_by_address(CITY,ORIGIN,DESTINATION):#输入是起点终点的地址
    ORIGIN_loc = get_location_geo(CITY,ORIGIN)
    DESTINATION_loc = get_location_geo(CITY,DESTINATION)
    return get_driving_path_distance_by_loc(ORIGIN_loc,DESTINATION_loc)




if __name__ == '__main__':
    # print(get_location_geo_json_info('北京市','朝阳区阜通东大街6号'))
    # print(get_location_regeo_info('116.480881,39.989410','json','1000','all'))    
    #把驾驶路径规划写入json文件
    # with open('use_GaoDe_api/path.json','w',encoding='utf-8') as f:
    #     f.write(json.dumps(get_driving_path_info('115.480881,39.989410','116.397499,39.908722'),ensure_ascii=False,indent=4))
    # origin = '上海荟聚'
    # destination = '上海迪士尼度假区'
    # origin_geo = get_location_geo('上海市',origin)
    # print(origin_geo)
    
    # destination_geo = get_location_geo('上海市',destination)
    # print(destination_geo)
    # distance = get_driving_path_distance_by_loc(origin_geo,destination_geo)
    # print(type(distance))

    # print('从{}到{}驾车距离为{}米'.format(origin,destination,distance))
    # distance = get_driving_path_distance_by_address('上海市',origin,destination)
    # print('从{}到{}驾车距离为{}米'.format(origin,destination,distance))
    #上海,新荣记(上海虹桥祥源希尔顿酒店店) 的经纬度
    CITY = '上海'
    ADDRESS = '北京大学'
    a=get_location_geo(CITY,ADDRESS)
    print(f"{CITY}市,{ADDRESS}的经纬度为{a}")
    