import streamlit as st
import pandas as pd
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class BaseModule(ABC):
    """所有功能模块的基类"""
    
    def __init__(
        self, 
        title: str, 
        description: str = "",
        width: int = 100,
        height: Optional[int] = None,
        background_color: Optional[str] = None,
        border: bool = True,
        expanded: bool = True
    ):
        """
        初始化模块
        
        参数:
            title: 模块标题
            description: 模块描述
            width: 模块宽度百分比 (0-100)
            height: 模块高度
            background_color: 背景颜色
            border: 是否显示边框
            expanded: 折叠面板是否默认展开
        """
        self.title = title
        self.description = description
        self.width = width
        self.height = height
        self.background_color = background_color
        self.border = border
        self.expanded = expanded
        self.data: Optional[pd.DataFrame] = None
        self.output: Optional[Any] = None
        
    def set_data(self, data: pd.DataFrame) -> None:
        """设置模块要处理的数据"""
        self.data = data
        
    @abstractmethod
    def process_data(self) -> None:
        """处理数据，子类必须实现此方法"""
        pass
    
    @abstractmethod
    def render_output(self) -> None:
        """渲染处理结果，子类必须实现此方法"""
        pass
    
    def _get_container_styles(self) -> Dict[str, str]:
        """获取容器样式"""
        styles = {
            "width": f"{self.width}%",
            "padding": "1rem",
            "box-sizing": "border-box"
        }
        
        if self.background_color:
            styles["background-color"] = self.background_color
            
        if self.border:
            styles["border"] = "1px solid #e0e0e0"
            styles["border-radius"] = "0.5rem"
            
        if self.height:
            styles["height"] = f"{self.height}px"
            styles["overflow-y"] = "auto"
            
        return styles
    
    def render(self) -> None:
        """渲染整个模块"""
        if self.data is None:
            return
            
        # 处理数据
        self.process_data()
        
        # 创建容器
        with st.expander(self.title, expanded=self.expanded):
            # 显示描述
            if self.description:
                st.write(self.description)
            
            # 创建带样式的容器
            container_style = self._get_container_styles()
            st.markdown(
                f"""
                <div style="{' '.join([f'{k}: {v};' for k, v in container_style.items()])}">
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # 渲染输出
            self.render_output()
    