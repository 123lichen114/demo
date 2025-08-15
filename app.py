import streamlit as st
import pandas as pd
from typing import List
from modules.base import BaseModule
from modules.data_overview import DataOverviewModule
from modules.data_statistics import DataStatisticsModule
from modules.data_visualization import DataVisualizationModule
from modules.navigation_visualization import NavigationVisualizationModule
from modules.navigation_map_module import NavigationMapModule
from utils.logger_setup import setup_logger
from utils.cache_manager import cache_manager  # 导入离线缓存管理器
#忽略警告
import warnings
warnings.filterwarnings("ignore")
# 初始化应用日志
logger = setup_logger()

class DashboardApp:
    """仪表盘应用主类"""
    
    def __init__(self):
        self.title = "可扩展数据仪表盘"
        self.subtitle = "上传CSV文件，通过多个模块进行数据分析"
        self.data = None
        self.current_filename = None
        self.modules: List[BaseModule] = []
        
        # 初始化模块
        self._initialize_modules()
        
    def _initialize_modules(self) -> None:
        """初始化所有功能模块"""
        self.modules = [
            NavigationVisualizationModule(width=100),
            NavigationMapModule(width=100)
        ]
        
    def _load_data(self) -> None:
        """加载用户上传的数据，集成离线缓存检查"""
        uploaded_file = st.file_uploader("上传CSV文件", type=["csv"])
        
        if uploaded_file is not None:
            try:
                # 获取文件名和文件内容
                filename = uploaded_file.name
                self.current_filename = filename
                
                # 读取数据
                df = pd.read_csv(uploaded_file)
                
                # 检查离线缓存是否有效
                if cache_manager.is_cache_valid(filename, df):
                    st.success(f"文件 '{filename}' 已从离线缓存加载！")
                    logger.info(f"从离线缓存加载文件: {filename}")
                else:
                    # 更新离线缓存
                    cache_manager.update_file_cache(filename, df)
                    st.success(f"文件 '{filename}' 上传并保存到离线缓存！")
                    logger.info(f"新文件保存到离线缓存: {filename}")
                
                # 将数据和文件名传递给所有模块
                self.data = df.copy()
                for module in self.modules:
                    module.set_data(self.data.copy(), filename)  # 传递文件名用于缓存
                
            except Exception as e:
                error_msg = f"文件读取错误: {str(e)}"
                st.error(error_msg)
                logger.error(error_msg, exc_info=True)
    
    def run(self) -> None:
        """运行仪表盘应用"""
        st.set_page_config(page_title=self.title, layout="wide")
        
        # 添加全局CSS样式
        st.markdown("""
        <style>
        .stExpanderHeader {
            font-size: 1.2rem;
            font-weight: bold;
        }
        .stMetric {
            background-color: #f9fafb;
            padding: 1rem;
            border-radius: 0.5rem;
        }
        .stDataFrame {
            border-radius: 0.5rem;
            border: 1px solid #f0f2f6;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # 页面标题
        st.title(self.title)
        st.write(self.subtitle)
        
        # 离线缓存管理控件
        col_cache, _ = st.columns([1, 5])
        with col_cache:
            if st.button("清除所有离线缓存"):
                cache_manager.clear_cache()
                st.success("所有离线缓存已清除")
        
        # 加载数据
        self._load_data()
        
        # 如果数据已加载，显示所有模块
        if self.data is not None:
            for module in self.modules:
                module.render()
                st.divider()  # 模块之间的分隔线

if __name__ == "__main__":
    app = DashboardApp()
    app.run()
