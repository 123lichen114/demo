import streamlit as st
import pandas as pd
import numpy as np
from .base import BaseModule

class DataStatisticsModule(BaseModule):
    """数据统计分析模块"""
    
    def __init__(self, **kwargs):
        super().__init__(
            title="数据统计分析",
            description="展示数值型列的统计信息",** kwargs
        )
        
    def process_data(self) -> None:
        """处理数据，计算统计信息"""
        if self.data is None:
            return
            
        # 只对数值型列进行统计
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns
        self.output = self.data[numeric_cols].describe()
    
    def render_output(self) -> None:
        """渲染统计信息"""
        if self.output is None:
            st.write("没有可统计的数值型数据")
            return
            
        st.dataframe(self.output)
        
        # 显示缺失值情况
        st.subheader("缺失值统计")
        missing_values = self.data.isnull().sum()
        missing_percentage = (missing_values / len(self.data)) * 100
        missing_df = pd.DataFrame({
            '缺失值数量': missing_values,
            '缺失值比例(%)': missing_percentage
        })
        st.dataframe(missing_df[missing_df['缺失值数量'] > 0])
    