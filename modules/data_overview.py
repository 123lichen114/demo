import streamlit as st
from typing import Optional
from .base import BaseModule

class DataOverviewModule(BaseModule):
    """数据概览模块"""
    
    def __init__(self, **kwargs):
        super().__init__(
            title="数据概览",
            description="展示数据集的基本信息和前几行数据",** kwargs
        )
        
    def process_data(self) -> None:
        """处理数据，获取基本信息"""
        if self.data is None:
            return
            
        self.output = {
            "shape": self.data.shape,
            "columns": self.data.columns.tolist(),
            "dtypes": self.data.dtypes.astype(str).to_dict(),
            "head": self.data.head()
        }
    
    def render_output(self) -> None:
        """渲染数据概览"""
        if not self.output:
            return
            
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"数据集形状: {self.output['shape'][0]} 行, {self.output['shape'][1]} 列")
        with col2:
            st.write(f"数据类型: {', '.join(set(self.output['dtypes'].values()))}")
            
        st.subheader("数据列信息")
        st.write(self.output['dtypes'])
        
        st.subheader("前5行数据")
        st.dataframe(self.output['head'])
    