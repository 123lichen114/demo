import streamlit as st
from typing import Optional
from .base import BaseModule
import pandas as pd
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
        if not self.output:
            return
            
        # 顶部关键信息卡片
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("总行数", self.output['shape'][0])
        with col2:
            st.metric("总列数", self.output['shape'][1])
        with col3:
            st.metric("数据类型", ', '.join(set(self.output['dtypes'].values())))
            
        # 使用标签页组织内容
        tab1, tab2 = st.tabs(["数据预览", "列信息"])
        
        with tab1:
            st.subheader("前5行数据")
            st.dataframe(
                self.output['head'],
                use_container_width=True,
                hide_index=True
            )
            
        with tab2:
            st.subheader("列信息详情")
            # 转换为DataFrame更美观地展示
            cols_info = pd.DataFrame(
                list(self.output['dtypes'].items()),
                columns=['列名', '数据类型']
            )
            st.dataframe(cols_info, use_container_width=True, hide_index=True)
    