# demo/utils/cache_utils.py
import streamlit as st
from Handle_csv.scenario.navigation.navigation_info import get_navigation_info

@st.cache_resource(show_spinner="正在处理导航基础数据...")
def cache_navigation_info(df):
    """缓存导航信息计算结果，避免重复调用get_navigation_info"""
    return get_navigation_info(df)

