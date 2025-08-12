import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List

# 设置中文字体
plt.rcParams["font.family"] = ["WenQuanYi Micro Hei", "Heiti TC"]
sns.set(font="Heiti TC", font_scale=1.0)

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


class DataOverviewModule(BaseModule):
    """数据概览模块"""
    
    def __init__(self, **kwargs):
        super().__init__(
            title="数据概览",
            description="展示数据集的基本信息和前几行数据",
           ** kwargs
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


class DataStatisticsModule(BaseModule):
    """数据统计分析模块"""
    
    def __init__(self, **kwargs):
        super().__init__(
            title="数据统计分析",
            description="展示数值型列的统计信息",
           ** kwargs
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


class DataVisualizationModule(BaseModule):
    """数据可视化模块"""
    
    def __init__(self, **kwargs):
        super().__init__(
            title="数据可视化",
            description="对数据进行可视化分析",
           ** kwargs
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


class DataFilterModule(BaseModule):
    """数据筛选模块"""
    
    def __init__(self, **kwargs):
        super().__init__(
            title="数据筛选",
            description="根据条件筛选数据",
           ** kwargs
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


class DashboardApp:
    """仪表盘应用主类"""
    
    def __init__(self):
        self.title = "可扩展数据仪表盘"
        self.subtitle = "上传CSV文件，通过多个模块进行数据分析"
        self.data: Optional[pd.DataFrame] = None
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
