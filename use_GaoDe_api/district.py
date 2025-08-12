from use_GaoDe_api.geo import get_location_regeo_info
def get_district(location:str):
    json_response = get_location_regeo_info(location)
    if json_response.get('status') == '1':
        addressComponent = json_response['regeocode']['addressComponent']
        
        return {'province': addressComponent['province'],
                'city': addressComponent['city'],
                'district': addressComponent['district'],
                'township': addressComponent['township']
        }
    else:
        print(f"请求失败：{json_response.get('info', '未知错误')}")
        return {
            'province': '',
            'city': '',
            'district': '',
            'township': ''
        }
    
if __name__ == '__main__':
    # 116.481488,39.990464
    print(get_district('116.481488,39.990464'))
