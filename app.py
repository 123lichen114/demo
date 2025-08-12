import streamlit as st
import pandas as pd
from typing import List
from modules.base import BaseModule
from modules.data_overview import DataOverviewModule
from modules.data_statistics import DataStatisticsModule
from modules.data_visualization import DataVisualizationModule
from modules.data_filter import DataFilterModule

class DashboardApp:
    """仪表盘应用主类"""
    
    def __init__(self):
        self.title = "可扩展数据仪表盘"
        self.subtitle = "上传CSV文件，通过多个模块进行数据分析"
        self.data: pd.DataFrame = None
        self.modules: List[BaseModule] = []
        
        # 初始化模块
        self._initialize_modules()
        
    def _initialize_modules(self) -> None:
        """初始化所有功能模块"""
        self.modules = [
            DataOverviewModule(width=100),
            DataStatisticsModule(width=100),
            DataVisualizationModule(width=100),
            DataFilterModule(width=100)
        ]
        
    def _load_data(self) -> None:
        """加载用户上传的数据"""
        uploaded_file = st.file_uploader("上传CSV文件", type=["csv"])
        
        if uploaded_file is not None:
            try:
                self.data = pd.read_csv(uploaded_file)
                st.success("文件上传成功！")
                
                # 将数据传递给所有模块
                for module in self.modules:
                    module.set_data(self.data.copy())
                    
            except Exception as e:
                st.error(f"文件读取错误: {str(e)}")
    
    def run(self) -> None:
        """运行仪表盘应用"""
        st.set_page_config(page_title=self.title, layout="wide")
        
        # 页面标题
        st.title(self.title)
        st.write(self.subtitle)
        
        # 加载数据
        self._load_data()
        
        # 如果数据已加载，显示所有模块
        if self.data is not None:
            # 可以在这里根据需要调整模块布局
            for module in self.modules:
                module.render()
                st.divider()  # 模块之间的分隔线


if __name__ == "__main__":
    app = DashboardApp()
    app.run()
    