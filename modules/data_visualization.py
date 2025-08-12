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
    
    def __init__(self, **kwargs):
        super().__init__(
            title="数据可视化",
            description="对数据进行可视化分析",** kwargs
        )
        
    def process_data(self) -> None:
        """准备可视化所需数据"""
        # 可视化不需要预处理，直接在渲染时处理
        pass
    
    def render_output(self) -> None:
        """渲染可视化图表"""
        if self.data is None:
            return
            
        # 选择要可视化的列
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns.tolist()
        if not numeric_cols:
            st.write("没有可可视化的数值型数据")
            return
            
        # 选择图表类型
        chart_type = st.selectbox(
            "选择图表类型",
            ["直方图", "散点图", "箱线图", "相关性热力图"]
        )
        
        if chart_type == "直方图":
            col = st.selectbox("选择列", numeric_cols)
            bins = st.slider("分箱数量", 5, 50, 20)
            
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.histplot(data=self.data, x=col, bins=bins, kde=True)
            ax.set_title(f"{col}的分布")
            st.pyplot(fig)
            
        elif chart_type == "散点图":
            col_x = st.selectbox("X轴", numeric_cols)
            col_y = st.selectbox("Y轴", numeric_cols, index=1 if len(numeric_cols) > 1 else 0)
            
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.scatterplot(data=self.data, x=col_x, y=col_y)
            ax.set_title(f"{col_x}与{col_y}的关系")
            st.pyplot(fig)
            
        elif chart_type == "箱线图":
            col = st.selectbox("选择列", numeric_cols)
            
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.boxplot(data=self.data, y=col)
            ax.set_title(f"{col}的箱线图")
            st.pyplot(fig)
            
        elif chart_type == "相关性热力图":
            if len(numeric_cols) < 2:
                st.write("需要至少两列数值型数据来绘制相关性热力图")
                return
                
            corr = self.data[numeric_cols].corr()
            
            fig, ax = plt.subplots(figsize=(10, 8))
            sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5)
            ax.set_title("特征相关性热力图")
            st.pyplot(fig)
    