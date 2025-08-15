import streamlit as st
import pandas as pd
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from utils.cache_manager import cache_manager
from utils.logger_setup import setup_logger
class BaseModule(ABC):
    """所有功能模块的基类"""
    # def __init__(
    #     self, 
    #     title: str, 
    #     description: str = "",
    #     width: int = 100,
    #     height: Optional[int] = None,
    #     background_color: Optional[str] = None,
    #     border: bool = True,
    #     expanded: bool = True
    # ):
    #     """
    #     初始化模块
        
    #     参数:
    #         title: 模块标题
    #         description: 模块描述
    #         width: 模块宽度百分比 (0-100)
    #         height: 模块高度
    #         background_color: 背景颜色
    #         border: 是否显示边框
    #         expanded: 折叠面板是否默认展开
    #     """
    #     self.title = title
    #     self.description = description
    #     self.width = width
    #     self.height = height
    #     self.background_color = background_color
    #     self.border = border
    #     self.expanded = expanded
    #     self.data: Optional[pd.DataFrame] = None
    #     self.output: Optional[Any] = None
        
    # def set_data(self, data: pd.DataFrame) -> None:
    #     """设置模块要处理的数据"""
    #     self.data = data

    def __init__(self, title: str, description: str, width: int = 100):
        self.title = title
        self.description = description
        self.width = width
        self.data: Optional[pd.DataFrame] = None
        self.filename: Optional[str] = None  # 关联的文件名
        self.background_color: Optional[str] = None
        self.border: bool = True
        self.height: Optional[int] = None
        self.logger = setup_logger()
    
    def set_data(self, data: pd.DataFrame, filename: Optional[str] = None) -> None:
        """设置模块数据并关联文件名"""
        self.data = data
        self.filename = filename
        self.process_data()  # 数据更新后自动处理
    
    def _get_cache_key(self, content_name: str) -> str:
        """生成统一的缓存键（模块名_内容名）"""
        module_name = self.__class__.__name__
        return f"{module_name}_{content_name}"
    
    def _get_cached_content(self, content_name: str) -> Optional[Any]:
        """从离线缓存获取内容"""
        if not self.filename:
            return None
        cache_key = self._get_cache_key(content_name)
        return cache_manager.get_content_cache(self.filename, cache_key)
    
    def _cache_content(self, content_name: str, content: Any) -> None:
        """将内容存入离线缓存"""
        if not self.filename:
            return
        cache_key = self._get_cache_key(content_name)
        cache_manager.set_content_cache(self.filename, cache_key, content) 
    @abstractmethod
    def process_data(self) -> None:
        """处理数据，子类必须实现此方法"""
        pass
    
    @abstractmethod
    def render_output(self) -> None:
        """渲染处理结果，子类必须实现此方法"""
        pass
    
    # 修改 BaseModule 的 _get_container_styles 方法
    def _get_container_styles(self):
        """获取容器样式"""
        styles = {
            "width": f"{self.width}%",
            "padding": "1.5rem",
            "box-sizing": "border-box",
            "margin-bottom": "1.5rem",
            "box-shadow": "0 4px 12px rgba(0, 0, 0, 0.05)",  # 轻微阴影
            "border-radius": "0.75rem",  # 更大圆角
            "transition": "all 0.3s ease"  # 过渡动画
        }
        
        if self.background_color:
            styles["background-color"] = self.background_color
        else:
            styles["background-color"] = "#ffffff"  # 默认白色背景
            
        if self.border:
            styles["border"] = "1px solid #f0f2f6"  # 更浅的边框
            
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
        with st.expander(self.title, expanded=True):
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
    