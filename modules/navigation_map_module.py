# demo/modules/navigation_map_module.py
import streamlit as st
import folium
from streamlit_folium import st_folium
from .base import BaseModule
from utils.cache_utils import cache_navigation_info
from Handle_csv.scenario.navigation.interactive_maps import create_daily_navigation_maps
import time

# 移除原有logger初始化

@st.cache_resource(show_spinner="正在生成导航地图...")
def cache_daily_maps(nav_data):
    return create_daily_navigation_maps(nav_data)

class NavigationMapModule(BaseModule):
    """导航路线地图可视化模块"""
    
    def __init__(self, **kwargs):
        super().__init__(
            title="导航路线地图",
            description="交互式展示每日导航路线和目的地",** kwargs
        )
        self.navi_info = None
        self.nav_data = None
        self.daily_maps = []
    
    def process_data(self) -> None:
        """处理数据并通过缓存获取结果"""
        if self.data is None:
            self.daily_maps = []
            return
            
        try:
            # 计时
            start_time = time.time()
            self.navi_info = cache_navigation_info(self.data)
            self.nav_data = self.navi_info.Get_json_info()['poi_info_list']
            self.daily_maps = cache_daily_maps(self.nav_data)
            end_time = time.time()
            self.logger.info(f"导航地图生成耗时: {end_time - start_time:.2f}秒")  # 修改为self.logger
            self.logger.info(f"成功加载 {len(self.daily_maps)} 张每日导航地图")  # 修改为self.logger
            
        except KeyError as e:
            error_msg = f"导航数据格式错误，缺少关键字段: {str(e)}"
            st.error(error_msg)
            self.logger.error(error_msg, exc_info=True)  # 修改为self.logger
            self.daily_maps = []
        except Exception as e:
            error_msg = f"处理导航地图数据时出错: {str(e)}"
            st.error(error_msg)
            self.logger.error(error_msg, exc_info=True)  # 修改为self.logger
            self.daily_maps = []
        self.output = self.daily_maps
    
    def render_output(self) -> None:
        """渲染交互式地图"""
        if not self.daily_maps:
            st.info("没有可显示的导航地图数据，请上传包含完整导航信息的CSV文件")
            return
            
        # 显示日期选择器（优化显示格式）
        date_options = [
            f"{map.location[0]:.4f}, {map.location[1]:.4f} - {i+1}天" 
            for i, map in enumerate(self.daily_maps)
        ]
        
        selected_idx = st.selectbox(
            "选择日期查看导航路线",
            range(len(date_options)),
            format_func=lambda x: date_options[x]
        )
        
        # 显示选中的地图（直接从缓存读取，无需重新生成）
        selected_map = self.daily_maps[selected_idx]
        st_folium(
            selected_map,
            width="100%",
            height=600,
            returned_objects=[]
        )
        
        # 显示地图说明
        st.caption("""
        地图说明:
        - 绿色标记: 起点
        - 蓝色标记: 中途目的地
        - 红色标记: 最终目的地
        - 橙色线: 导航路线
        - 点击标记可查看详细信息
        """)