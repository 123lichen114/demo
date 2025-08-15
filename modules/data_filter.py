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
        if self.data is None:
            return
            
        st.write("### 数据筛选器")
        st.caption("根据条件筛选数据，支持多维度组合筛选")
        
        # 使用折叠面板收纳筛选条件
        with st.expander("筛选条件设置", expanded=True):
            # 支持多列筛选
            filter_cols = st.multiselect(
                "选择需要筛选的列（可多选）",
                self.data.columns,
                default=[self.data.columns[0]] if len(self.data.columns) > 0 else []
            )
            
            filters = []
            for col in filter_cols:
                col_data = self.data[col]
                st.write(f"#### 筛选：{col}")
                
                if pd.api.types.is_numeric_dtype(col_data):
                    min_val = float(col_data.min())
                    max_val = float(col_data.max())
                    val_range = st.slider(
                        f"{col}的范围",
                        min_val, max_val, (min_val, max_val)
                    )
                    filters.append((col, "range", val_range))
                    
                # 其他类型处理...
        
        # 应用筛选
        if filters:
            self.filtered_data = self.data.copy()
            for col, filter_type, value in filters:
                if filter_type == "range":
                    self.filtered_data = self.filtered_data[
                        (self.filtered_data[col] >= value[0]) & 
                        (self.filtered_data[col] <= value[1])
                    ]
            
            # 筛选结果展示
            st.success(f"筛选完成：{len(self.filtered_data)} 行数据（原始：{len(self.data)}行）")
            st.dataframe(self.filtered_data, use_container_width=True)
            
            # 下载按钮美化
            csv = self.filtered_data.to_csv(index=False)
            st.download_button(
                label="📥 下载筛选后的数据",
                data=csv,
                file_name="filtered_data.csv",
                mime="text/csv",
                use_container_width=True
            )
        