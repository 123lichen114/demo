import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from .base import BaseModule

# 设置中文字体
plt.rcParams["font.family"] = ["WenQuanYi Micro Hei", "Heiti TC"]
sns.set(font="Heiti TC", font_scale=1.0)

class DataVisualizationModule(BaseModule):
    """数据可视化模块"""
    
    # 在类初始化时添加图表风格设置
    def __init__(self, **kwargs):
        super().__init__(
            title="数据可视化",
            description="对数据进行可视化分析",** kwargs
        )
        # 设置统一图表风格
        plt.style.use('seaborn-v0_8-whitegrid')
        sns.set_palette("husl")  # 更和谐的色调

    # 优化图表渲染部分，添加标题样式和交互说明
    def render_output(self) -> None:
        if self.data is None:
            return
            
        # 使用两列布局，左侧选项，右侧图表
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.write("### 图表设置")
            numeric_cols = self.data.select_dtypes(include=[np.number]).columns.tolist()
            if not numeric_cols:
                st.info("没有可可视化的数值型数据")
                return
                
            chart_type = st.selectbox(
                "选择图表类型",
                ["直方图", "散点图", "箱线图", "相关性热力图"]
            )
            
            # 根据图表类型显示相应配置
            configs = {}
            if chart_type == "直方图":
                configs["col"] = st.selectbox("选择列", numeric_cols)
                configs["bins"] = st.slider("分箱数量", 5, 50, 20)
            elif chart_type == "散点图":
                configs["col_x"] = st.selectbox("X轴", numeric_cols)
                configs["col_y"] = st.selectbox("Y轴", numeric_cols, 
                                            index=1 if len(numeric_cols) > 1 else 0)
            elif chart_type == "箱线图":
                configs["col"] = st.selectbox("选择列", numeric_cols)
        
        with col2:
            st.write(f"### {chart_type} 展示")
            if chart_type == "直方图":
                fig, ax = plt.subplots(figsize=(10, 6))
                sns.histplot(data=self.data, x=configs["col"], bins=configs["bins"], kde=True)
                ax.set_title(f"{configs['col']}的分布", fontsize=14, pad=20)
                ax.set_xlabel(configs["col"], fontsize=12)
                ax.set_ylabel("频数", fontsize=12)
                st.pyplot(fig)
                
            # 其他图表类型类似处理...
            # 添加图表说明
            st.caption("提示：点击图表可放大查看，双击可重置")
        
    def process_data(self) -> None:
        """准备可视化所需数据"""
        # 可视化不需要预处理，直接在渲染时处理
        pass
    
    
    