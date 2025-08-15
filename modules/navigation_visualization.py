import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from .base import BaseModule
# 替换直接导入，使用缓存版本
from utils.cache_utils import cache_navigation_info
from Handle_csv.handle import get_target_info
from Handle_csv.scenario.navigation.origin_destination_heatmap import plot_origin_destination_heatmap
from Handle_csv.scenario.navigation.visualization import (
    plot_destination_time_heatmap,
    plot_destination_type_pie
)
from utils.logger_setup import setup_logger

# 初始化模块专用日志
logger = setup_logger()

# 新增：缓存可视化相关计算（如果有重复调用的绘图函数）
@st.cache_resource(show_spinner="正在生成路线时间线...")
def cache_route_timeline(navi_info):
    return get_target_info(navi_info, 'nagivation_draw')

class NavigationVisualizationModule(BaseModule):
    """导航数据可视化模块"""
    
    def __init__(self, **kwargs):
        super().__init__(
            title="导航数据分析",
            description="分析和可视化导航相关数据",** kwargs
        )
        self.navi_info = None
        self.nav_data = None
        self.json_data = None  # 存储JSON数据用于后续展示
    
    def process_data(self) -> None:
        """处理导航数据（使用缓存结果）"""
        if self.data is None:
            return
            
        # 获取导航信息（使用缓存，避免重复计算）
        try:
            self.navi_info = cache_navigation_info(self.data)
            self.nav_data = self.navi_info.Get_json_info()['poi_info_list']
            self.json_data = self.navi_info.Get_json_info()  # 保存JSON数据
            logger.info("导航数据处理成功")
        except Exception as e:
            error_msg = f"处理导航数据时出错: {str(e)}"
            st.error(error_msg)
            logger.error(error_msg, exc_info=True)
            self.navi_info = None
            self.nav_data = None
            self.json_data = None
    
    def render_output(self) -> None:
        """渲染导航数据可视化结果"""
        if self.data is None or self.navi_info is None or self.nav_data is None:
            st.info("请先上传包含导航数据的CSV文件")
            return
            
        # 显示基本导航信息
        st.subheader("导航基本信息")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("目的地数量", len(self.nav_data))
        with col2:
            st.metric("用户居住地", self.navi_info.home if self.navi_info.home else "未知")
        
        try:
            # 左侧：导航数据详情
            left_col, right_col = st.columns(2, gap="large")
            container_height = 500
            
            with left_col:
                st.subheader("导航数据详情")
                with st.container(height=container_height):
                    st.json(self.json_data, expanded=False)
            
            # 右侧：用户基本特征标签表格
            with right_col:
                st.subheader("用户基本特征标签")
                # 使用缓存减少重复计算
                feature_label = get_target_info(self.navi_info, 'user_basic_feature_label')
                labels = feature_label.show_basic_feature_label()     
                labels_df = pd.DataFrame(
                    list(labels.items()),
                    columns=["特征", "值"]
                )
                with st.container(height=container_height):
                    if labels_df.empty:
                        st.info("暂无用户特征标签数据")
                    else:
                        st.dataframe(
                            labels_df,
                            use_container_width=True,
                            hide_index=True
                        )
            
            # 路线时间线（使用缓存）
            st.subheader("导航数据可视化")
            row1_col1, row1_col2 = st.columns(2, gap="medium")
            
            with row1_col1:
                with st.container(height=400):
                    st.subheader("路线时间线")
                    # 使用缓存的路线时间线结果
                    plot_buf = cache_route_timeline(self.navi_info)
                    if plot_buf:
                        st.image(plot_buf, use_column_width=True)
                    else:
                        st.info("暂无路线时间线数据")
            
            with row1_col2:
                with st.container(height=400):
                    st.subheader("起点-终点热力图")
                    grid_size = st.slider("网格大小(米)", 100, 500, 200)
                    try:
                        df = plot_origin_destination_heatmap(self.nav_data, grid_size)
                        st.pyplot(plt.gcf())
                        with st.expander("查看详细数据"):
                            st.dataframe(df)
                    except Exception as e:
                        error_msg = f"生成热力图时出错: {str(e)}"
                        st.error(error_msg)
                        logger.error(error_msg, exc_info=True)
            
            # 第二行图表：目的地与时间段热力图和目的地类型分布
            row2_col1, row2_col2 = st.columns(2, gap="medium")
            
            with row2_col1:
                with st.container(height=400):
                    st.subheader("目的地与时间段热力图")
                    st.caption("展示不同时间段各目的地的访问频率")
                    try:
                        plot_destination_time_heatmap(self.nav_data)
                        st.pyplot(plt.gcf())
                    except Exception as e:
                        error_msg = f"生成热力图时出错: {str(e)}"
                        st.error(error_msg)
                        logger.error(error_msg, exc_info=True)
            
            with row2_col2:
                with st.container(height=400):
                    st.subheader("目的地类型分布")
                    st.caption("展示不同类型目的地的占比情况")
                    try:
                        plot_destination_type_pie(self.nav_data)
                        st.pyplot(plt.gcf())
                    except Exception as e:
                        error_msg = f"生成饼状图时出错: {str(e)}"
                        st.error(error_msg)
                        logger.error(error_msg, exc_info=True)
            
            # # 第三行图表：起点-终点热力图
            # with st.container(height=500):
            #     st.subheader("起点-终点热力图")
            #     grid_size = st.slider("网格大小(米)", 100, 500, 200)
            #     try:
            #         df = plot_origin_destination_heatmap(self.nav_data, grid_size)
            #         st.pyplot(plt.gcf())
            #         with st.expander("查看详细数据"):
            #             st.dataframe(df)
            #     except Exception as e:
            #         error_msg = f"生成热力图时出错: {str(e)}"
            #         st.error(error_msg)
            #         logger.error(error_msg, exc_info=True)
                    
        except Exception as e:
            error_msg = f"导航数据可视化失败: {str(e)}"
            st.error(error_msg)
            logger.error(error_msg, exc_info=True)
