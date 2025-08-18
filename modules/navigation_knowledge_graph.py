import streamlit as st
import pandas as pd
from io import BytesIO
from .base import BaseModule
from utils.cache_utils import cache_navigation_info
from Handle_csv.scenario.navigation.knowledge_graph import NavigationKnowledgeGraph

class NavigationKnowledgeGraphModule(BaseModule):
    """导航知识图谱可视化与预测模块"""
    
    def __init__(self, **kwargs):
        super().__init__(
            title="导航知识图谱与智能预测",
            description="展示导航实体关系图谱及预测性导航分析",** kwargs
        )
        self.navi_info = None
        self.nav_data = None
        self.kg = None
        self.visualization_buf = None
        self.prediction_features = None
    
    def process_data(self) -> None:
        """处理数据并构建知识图谱"""
        if self.data is None:
            return
        
        try:
            # 获取导航信息（复用现有缓存逻辑）
            self.navi_info = cache_navigation_info(self.data)
            self.nav_data = self.navi_info.Get_json_info()['poi_info_list']
            
            # 构建知识图谱
            self.kg = NavigationKnowledgeGraph(user_id="current_user")
            self.kg.build_from_json_info(self.nav_data)
            
            # 提取预测特征
            self.prediction_features = self.kg.get_prediction_features()
            
            # 生成可视化
            self.visualization_buf = self.kg.generate_visualization()
            
            self.logger.info("导航知识图谱构建成功")
        except Exception as e:
            error_msg = f"构建知识图谱失败: {str(e)}"
            st.error(error_msg)
            self.logger.error(error_msg, exc_info=True)
    
    def render_prediction_analysis(self) -> None:
        """渲染预测性导航分析结果"""
        st.subheader("智能导航预测分析")
        
        if not self.prediction_features:
            st.info("暂无足够数据进行预测分析")
            return
        
        # 1. 高频访问地点
        loc_freq = self.prediction_features["location_frequency"]
        if loc_freq:
            loc_df = pd.DataFrame(
                [(self.kg.graph.nodes[loc]["label"], freq) for loc, freq in loc_freq.items()],
                columns=["地点", "访问频率"]
            ).sort_values(by="访问频率", ascending=False)
            
            with st.expander("高频访问地点（预测基础）", expanded=True):
                st.dataframe(loc_df, use_container_width=True, hide_index=True)
        
        # 2. 出行时间分布
        hour_dist = self.prediction_features["hour_distribution"]
        if hour_dist:
            hour_df = pd.DataFrame(
                [(f"{h}:00-{h+1}:00", cnt) for h, cnt in hour_dist.items()],
                columns=["时间段", "出行次数"]
            ).sort_values(by="时间段")
            
            with st.expander("出行时间分布", expanded=True):
                st.bar_chart(hour_df.set_index("时间段"))
        
        # 3. 智能提醒建议
        st.subheader("智能导航提醒建议")
        try:
            # 基于高频地点和时间生成建议
            top_loc = max(loc_freq.items(), key=lambda x: x[1])[0] if loc_freq else None
            peak_hour = max(hour_dist.items(), key=lambda x: x[1])[0] if hour_dist else None
            
            if top_loc and peak_hour:
                loc_name = self.kg.graph.nodes[top_loc]["label"]
                st.info(f"根据历史数据，您通常在 {peak_hour}:00 左右前往 {loc_name}，建议提前规划路线")
            else:
                st.info("积累更多导航数据后，将为您提供个性化提醒")
        except Exception as e:
            st.warning(f"生成建议时出错: {str(e)}")
    
    def render_output(self) -> None:
        """渲染模块输出"""
        if self.data is None or not self.kg or not self.visualization_buf:
            st.info("请上传包含导航数据的CSV文件以生成知识图谱")
            return
        
        # 图谱可视化
        st.subheader("导航知识图谱可视化")
        st.caption("实体类型: 用户(蓝) | 地点(绿) | 时间(黄) | 导航事件(红)")
        st.components.v1.html(self.visualization_buf.getvalue().decode(), height=600)
        
        # 预测分析
        self.render_prediction_analysis()
        
        # 导出功能
        col1, col2 = st.columns(2)
        with col1:
            if st.button("导出图谱数据(JSON)"):
                buf = BytesIO()
                self.kg.export_to_json(buf)
                st.download_button(
                    "下载JSON文件",
                    data=buf,
                    file_name=f"navigation_kg_{self.current_filename}.json",
                    mime="application/json"
                )