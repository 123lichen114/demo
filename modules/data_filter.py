import streamlit as st
import pandas as pd
import numpy as np
from .base import BaseModule

class DataFilterModule(BaseModule):
    """数据筛选模块"""
    
    def __init__(self, **kwargs):
        super().__init__(
            title="数据筛选",
            description="根据条件筛选数据",** kwargs
        )
        self.filtered_data = None
        
    def process_data(self) -> None:
        """处理数据筛选"""
        # 筛选在渲染时处理
        pass
    
    def render_output(self) -> None:
        """渲染筛选界面和结果"""
        if self.data is None:
            return
            
        st.write("选择筛选条件:")
        
        # 选择要筛选的列
        filter_col = st.selectbox("选择列", self.data.columns)
        
        # 根据列类型显示不同的筛选控件
        col_data = self.data[filter_col]
        
        if pd.api.types.is_numeric_dtype(col_data):
            # 数值型列
            min_val = float(col_data.min())
            max_val = float(col_data.max())
            val_range = st.slider(
                f"选择{filter_col}的范围",
                min_val, max_val, (min_val, max_val)
            )
            self.filtered_data = self.data[(col_data >= val_range[0]) & (col_data <= val_range[1])]
            
        elif pd.api.types.is_datetime64_any_dtype(col_data):
            # 日期型列
            min_date = col_data.min()
            max_date = col_data.max()
            date_range = st.date_input(
                f"选择{filter_col}的范围",
                [min_date, max_date]
            )
            if len(date_range) == 2:
                self.filtered_data = self.data[(col_data >= pd.Timestamp(date_range[0])) & 
                                              (col_data <= pd.Timestamp(date_range[1]))]
            else:
                self.filtered_data = self.data.copy()
                
        else:
            # 类别型列
            unique_vals = col_data.unique()
            selected_vals = st.multiselect(
                f"选择{filter_col}的值",
                unique_vals,
                default=list(unique_vals)
            )
            self.filtered_data = self.data[col_data.isin(selected_vals)]
            
        # 显示筛选结果
        st.write(f"筛选后的数据: {len(self.filtered_data)} 行")
        st.dataframe(self.filtered_data)
        
        # 提供下载筛选后数据的选项
        csv = self.filtered_data.to_csv(index=False)
        st.download_button(
            label="下载筛选后的数据",
            data=csv,
            file_name="filtered_data.csv",
            mime="text/csv",
        )
    