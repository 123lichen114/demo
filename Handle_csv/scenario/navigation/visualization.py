import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Any
from io import BytesIO,StringIO
import json 
import igraph as ig
from pyvis.network import Network
from datetime import datetime
import os 
import tempfile
# 渲染自定义HTML
import cairo
# 设置中文字体
plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["font.family"] = ["Heiti TC"]
plt.rcParams["axes.unicode_minus"] = False

def plot_destination_time_heatmap(nav_data: List[Dict[str, Any]]) -> None:
    """
    绘制目的地与时间段相关性热力图
    
    参数:
        nav_data: 导航数据列表，包含目的地和时间信息
    """
    if not nav_data:
        raise ValueError("导航数据为空，无法绘制热力图")  # 检查输入数据是否为空
        
    # 转换数据格式，将列表形式的导航数据转换为DataFrame格式
    df = pd.DataFrame(nav_data)
    
    # 提取日期和小时信息
    if 'start_time' not in df.columns:
        raise KeyError("导航数据缺少'start_time'字段")
        
    # 确保时间列是datetime类型
    df['start_time'] = pd.to_datetime(df['start_time'], errors='coerce')
    df = df.dropna(subset=['start_time'])
    
    # 提取小时和目的地名称
    df['hour'] = df['start_time'].dt.hour
    df['poi'] = df.get('poi', df.get('poi_name', '未知'))
    
    # 统计每个目的地在每个小时的出现次数
    heatmap_data = df.groupby(['poi', 'hour']).size().unstack(fill_value=0)
    
    # 创建热力图
    plt.figure(figsize=(12, 8))
    sns.heatmap(heatmap_data, cmap="YlOrRd", annot=True, fmt="d", cbar_kws={'label': '出现次数'})
    plt.title('目的地与时间段相关性热力图', fontsize=15)
    plt.xlabel('时间段（小时）', fontsize=12)
    plt.ylabel('目的地', fontsize=12)
    plt.tight_layout()
    

def plot_destination_type_pie(nav_data: List[Dict[str, Any]]) -> None:
    """
    绘制目的地类型饼状图
    
    参数:
        nav_data: 导航数据列表，包含目的地类型信息
    """
    if not nav_data:
        raise ValueError("导航数据为空，无法绘制饼状图")
        
    # 转换数据格式
    df = pd.DataFrame(nav_data)
    
    # 提取目的地类型
    type_column = 'type'
    
    # 统计各类型数量
    type_counts = df[type_column].value_counts()
    
    # 合并占比过小的类型
    threshold = 0.03  # 3%阈值
    type_counts = type_counts / type_counts.sum()
    small_types = type_counts[type_counts < threshold].sum()
    type_counts = type_counts[type_counts >= threshold]
    if small_types > 0:
        type_counts['其他'] = small_types
    
    # 创建饼状图
    plt.figure(figsize=(10, 8))
    wedges, texts, autotexts = plt.pie(
        type_counts, 
        labels=type_counts.index,
        autopct='%1.1f%%',
        startangle=140,
        wedgeprops=dict(width=0.4)  # 环形图效果
    )
    
    # 美化文本
    plt.setp(texts, size=12)
    plt.setp(autotexts, size=10, color="black", weight="bold")
    plt.title('目的地类型分布', fontsize=15)
    plt.tight_layout()

# def generate_kg_visualization(self) -> BytesIO:
#         """使用igraph实现支持折叠/展开的导航图谱（修复未定义变量问题）"""
#         # 1. 初始化所有可能用到的变量，避免未定义错误
#         user_node = None
#         user_id = "user_node"  # 统一用户节点标识
#         event_details = []
#         ig_graph = None
#         layout = None
#         has_more = False
#         visible_events = []
#         hidden_events = []
        
#         # 提取并排序导航事件
#         try:
#             for node, data in self.graph.nodes(data=True):
#                 if data.get("entity_type") == "用户":
#                     user_node = node
#                     user_id = node
#                 elif data.get("entity_type") == "导航事件":
#                     # 收集事件关联信息
#                     start_time_node = None
#                     end_time_node = None
#                     start_loc_node = None
#                     end_loc_node = None
                    
#                     # 确保图中有边数据再进行遍历
#                     if self.graph.out_edges(node):
#                         for _, end_node, edge_data in self.graph.out_edges(node, data=True):
#                             rel = edge_data.get("relation")
#                             if rel == "开始于":
#                                 start_time_node = end_node
#                             elif rel == "结束于":
#                                 end_time_node = end_node
#                             elif rel == "从...出发":
#                                 start_loc_node = end_node
#                             elif rel == "前往...":
#                                 end_loc_node = end_node
                    
#                     if start_time_node:
#                         time_data = self.graph.nodes.get(start_time_node, {})
#                         try:
#                             time_str = time_data.get("label", "").split('.')[0]
#                             time_obj = datetime.fromisoformat(time_str)
#                             event_details.append({
#                                 "event_node": node,
#                                 "time_obj": time_obj,
#                                 "start_time": start_time_node,
#                                 "end_time": end_time_node,
#                                 "start_loc": start_loc_node,
#                                 "end_loc": end_loc_node,
#                                 "label": self.graph.nodes[node].get("label", f"事件{len(event_details)}")
#                             })
#                         except Exception:
#                             continue
            
#             # 处理事件排序和显示逻辑
#             event_details.sort(key=lambda x: x["time_obj"])
#             event_count = len(event_details)
#             max_display = 7
#             has_more = event_count > max_display
#             visible_events = event_details[:max_display] if event_count > 0 else []
#             hidden_events = event_details[max_display:] if has_more else []
            
#             # 2. 构建igraph图
#             ig_graph = ig.Graph(directed=True)
            
#             # 节点映射（原始节点ID -> igraph顶点ID）
#             node_mapping = {}
#             all_nodes = [user_id]  # 确保用户节点在首位
            
#             # 添加可见节点
#             for detail in visible_events:
#                 all_nodes.append(detail["event_node"])
#                 if detail["start_time"]:
#                     all_nodes.append(detail["start_time"])
#                 if detail["end_time"]:
#                     all_nodes.append(detail["end_time"])
#                 if detail["start_loc"]:
#                     all_nodes.append(detail["start_loc"])
#                 if detail["end_loc"]:
#                     all_nodes.append(detail["end_loc"])
            
#             # 添加折叠标记（如果需要）
#             collapse_node = "collapse_marker"
#             if has_more:
#                 all_nodes.append(collapse_node)
            
#             # 添加隐藏事件的节点引用
#             for detail in hidden_events:
#                 all_nodes.append(detail["event_node"])
            
#             # 去重并创建映射
#             unique_nodes = list(dict.fromkeys(all_nodes))
#             for idx, node in enumerate(unique_nodes):
#                 node_mapping[node] = idx
            
#             # 添加顶点
#             ig_graph.add_vertices(len(unique_nodes))
            
#             # 3. 设置节点属性
#             colors = []
#             sizes = []
#             labels = []
#             shapes = []
#             visible = []
            
#             # 样式配置
#             color_scheme = {
#                 "用户": "#2c3e50",
#                 "导航事件": "#e74c3c",
#                 "时间": "#f1c40f",
#                 "地点": "#3498db",
#                 "折叠标记": "#9b59b6",
#                 "未知": "#95a5a6"
#             }
            
#             size_scheme = {
#                 "用户": 30,
#                 "导航事件": 20,
#                 "时间": 15,
#                 "地点": 15,
#                 "折叠标记": 18,
#                 "未知": 12
#             }
            
#             shape_scheme = {
#                 "用户": "circle",
#                 "导航事件": "diamond",
#                 "时间": "triangle-up",
#                 "地点": "square",
#                 "折叠标记": "star",
#                 "未知": "circle"
#             }
            
#             for node in unique_nodes:
#                 # 确定节点类型
#                 if node == user_id:
#                     entity_type = "用户"
#                     node_label = self.graph.nodes.get(node, {}).get("label", "用户")
#                     is_visible = True
#                 elif node == collapse_node:
#                     entity_type = "折叠标记"
#                     node_label = f"...还有{len(hidden_events)}个事件"
#                     is_visible = True
#                 elif any(node == d["event_node"] for d in visible_events):
#                     entity_type = "导航事件"
#                     # 使用列表推导式避免next可能的StopIteration
#                     matching = [d["label"] for d in visible_events if d["event_node"] == node]
#                     node_label = matching[0] if matching else f"事件{node}"
#                     is_visible = True
#                 elif any(node == d["event_node"] for d in hidden_events):
#                     entity_type = "导航事件"
#                     matching = [d["label"] for d in hidden_events if d["event_node"] == node]
#                     node_label = matching[0] if matching else f"事件{node}"
#                     is_visible = False  # 隐藏事件默认不可见
#                 elif any(node in [d["start_time"], d["end_time"]] for d in visible_events):
#                     entity_type = "时间"
#                     node_label = self.graph.nodes.get(node, {}).get("label", "时间")[:10]
#                     is_visible = False  # 时间默认隐藏
#                 elif any(node in [d["start_loc"], d["end_loc"]] for d in visible_events):
#                     entity_type = "地点"
#                     node_label = self.graph.nodes.get(node, {}).get("label", "地点")
#                     is_visible = False  # 地点默认隐藏
#                 else:
#                     entity_type = "未知"
#                     node_label = str(node)
#                     is_visible = False
                
#                 colors.append(color_scheme[entity_type])
#                 sizes.append(size_scheme[entity_type])
#                 labels.append(node_label)
#                 shapes.append(shape_scheme[entity_type])
#                 visible.append(is_visible)
            
#             # 设置顶点属性
#             ig_graph.vs["color"] = colors
#             ig_graph.vs["size"] = sizes
#             ig_graph.vs["label"] = labels
#             ig_graph.vs["shape"] = shapes
#             ig_graph.vs["visible"] = visible
#             ig_graph.vs["entity_type"] = [
#                 "用户" if n == user_id else
#                 "折叠标记" if n == collapse_node else
#                 "导航事件" if any(n == d["event_node"] for d in event_details) else
#                 "时间" if any(n in [d["start_time"], d["end_time"]] for d in event_details) else
#                 "地点" if any(n in [d["start_loc"], d["end_loc"]] for d in event_details) else
#                 "未知"
#                 for n in unique_nodes
#             ]
            
#             # 4. 添加边
#             edges = []
#             edge_labels = []
#             edge_visible = []
            
#             # 用户到可见事件的边
#             for detail in visible_events:
#                 u = node_mapping.get(user_id)
#                 v = node_mapping.get(detail["event_node"])
#                 if u is not None and v is not None:
#                     edges.append((u, v))
#                     edge_labels.append("包含")
#                     edge_visible.append(True)
            
#             # 用户到折叠标记的边
#             if has_more:
#                 u = node_mapping.get(user_id)
#                 v = node_mapping.get(collapse_node)
#                 if u is not None and v is not None:
#                     edges.append((u, v))
#                     edge_labels.append(f"还有{len(hidden_events)}个")
#                     edge_visible.append(True)
            
#             # 事件到时间/地点的边
#             for detail in visible_events:
#                 event_v = node_mapping.get(detail["event_node"])
#                 if event_v is None:
#                     continue
                    
#                 # 开始时间
#                 if detail["start_time"] and detail["start_time"] in node_mapping:
#                     time_v = node_mapping[detail["start_time"]]
#                     edges.append((event_v, time_v))
#                     edge_labels.append("开始于")
#                     edge_visible.append(False)
                
#                 # 结束时间
#                 if detail["end_time"] and detail["end_time"] in node_mapping:
#                     time_v = node_mapping[detail["end_time"]]
#                     edges.append((event_v, time_v))
#                     edge_labels.append("结束于")
#                     edge_visible.append(False)
                
#                 # 开始地点
#                 if detail["start_loc"] and detail["start_loc"] in node_mapping:
#                     loc_v = node_mapping[detail["start_loc"]]
#                     edges.append((event_v, loc_v))
#                     edge_labels.append("从...出发")
#                     edge_visible.append(False)
                
#                 # 结束地点
#                 if detail["end_loc"] and detail["end_loc"] in node_mapping:
#                     loc_v = node_mapping[detail["end_loc"]]
#                     edges.append((event_v, loc_v))
#                     edge_labels.append("前往...")
#                     edge_visible.append(False)
            
#             # 添加隐藏事件的边
#             for detail in hidden_events:
#                 u = node_mapping.get(user_id)
#                 v = node_mapping.get(detail["event_node"])
#                 if u is not None and v is not None:
#                     edges.append((u, v))
#                     edge_labels.append("包含")
#                     edge_visible.append(False)
            
#             ig_graph.add_edges(edges)
#             ig_graph.es["label"] = edge_labels
#             ig_graph.es["visible"] = edge_visible
#             ig_graph.es["color"] = "#7f8c8d"
#             ig_graph.es["width"] = 1.5
            
#             # 5. 布局设置
#             if node_mapping.get(user_id) is not None:
#                 layout = ig_graph.layout_reingold_tilford(root=[node_mapping[user_id]])
#                 # 调整布局
#                 for i in range(len(layout)):
#                     x, y = layout[i]
#                     layout[i] = (x * 30, -y * 60)
#             else:
#                 #  fallback布局，避免layout未定义
#                 layout = ig_graph.layout_kamada_kawai()
            
#             # 6. 自定义HTML模板和CSS样式
#             custom_css = """
#             <style>
#                 .node { cursor: pointer; }
#                 .node text { font-size: 10px; }
#                 .edge { stroke-opacity: 0.6; }
#                 .edge text { font-size: 8px; fill: #555; }
#                 .node circle, .node ellipse, .node polygon, .node path {
#                     stroke: #fff;
#                     stroke-width: 1px;
#                 }
#                 svg { max-width: 100%; }
#             </style>
#             """
            
#             template = """
#             <html>
#             <head>
#                 <meta charset="utf-8">
#                 <title>导航知识图谱</title>
#                 {{ custom_css }}
#                 <style>
#                     .controls {
#                         position: absolute;
#                         top: 10px;
#                         left: 50%;
#                         transform: translateX(-50%);
#                         z-index: 100;
#                         background: white;
#                         padding: 8px;
#                         border-radius: 4px;
#                         box-shadow: 0 1px 3px rgba(0,0,0,0.1);
#                     }
#                     button {
#                         margin: 0 5px;
#                         padding: 6px 12px;
#                         border: none;
#                         border-radius: 4px;
#                         background: #3498db;
#                         color: white;
#                         cursor: pointer;
#                     }
#                     button:hover {
#                         background: #2980b9;
#                     }
#                     .graph-container {
#                         width: 100%;
#                         overflow: auto;
#                         position: relative;
#                         height: 800px;
#                     }
#                 </style>
#             </head>
#             <body>
#                 <div class="controls">
#                     <button id="toggleDetails">显示时间地点</button>
#                     {% if has_more %}
#                     <button id="toggleEvents">展开全部事件</button>
#                     {% endif %}
#                 </div>
#                 <div class="graph-container">
#                     {{ svg_content }}
#                 </div>
#                 <script>
#                     // 显示/隐藏时间地点
#                     document.getElementById("toggleDetails").addEventListener("click", function() {
#                         var nodes = document.querySelectorAll("g.node");
#                         var edges = document.querySelectorAll("g.edge");
                        
#                         nodes.forEach(function(node) {
#                             var id = node.getAttribute("data-id");
#                             var vertex = {{ graph_data }}.vertices[id];
#                             if (vertex.entity_type === "时间" || vertex.entity_type === "地点") {
#                                 node.style.display = node.style.display === "none" ? "block" : "none";
#                             }
#                         });
                        
#                         edges.forEach(function(edge, idx) {
#                             var edgeData = {{ graph_data }}.edges[idx];
#                             if (edgeData.label === "开始于" || edgeData.label === "结束于" || 
#                                 edgeData.label === "从...出发" || edgeData.label === "前往...") {
#                                 edge.style.display = edge.style.display === "none" ? "block" : "none";
#                             }
#                         });
#                     });
                    
#                     // 展开/折叠事件
#                     {% if has_more %}
#                     document.getElementById("toggleEvents").addEventListener("click", function() {
#                         var nodes = document.querySelectorAll("g.node");
#                         var edges = document.querySelectorAll("g.edge");
                        
#                         nodes.forEach(function(node) {
#                             var id = node.getAttribute("data-id");
#                             var vertex = {{ graph_data }}.vertices[id];
#                             if (vertex.entity_type === "导航事件" && !vertex.visible) {
#                                 node.style.display = node.style.display === "none" ? "block" : "none";
#                             }
#                             if (vertex.entity_type === "折叠标记") {
#                                 node.style.display = node.style.display === "none" ? "block" : "none";
#                             }
#                         });
                        
#                         edges.forEach(function(edge, idx) {
#                             var edgeData = {{ graph_data }}.edges[idx];
#                             if (!edgeData.visible) {
#                                 edge.style.display = edge.style.display === "none" ? "block" : "none";
#                             }
#                         });
#                     });
#                     {% endif %}
#                 </script>
#             </body>
#             </html>
#             """
            
#             # 准备图表数据用于前端交互
#             graph_data = {
#                 "vertices": [
#                     {
#                         "id": i,
#                         "entity_type": ig_graph.vs[i]["entity_type"],
#                         "visible": ig_graph.vs[i]["visible"]
#                     } for i in range(len(ig_graph.vs))
#                 ] if ig_graph and len(ig_graph.vs) > 0 else [],
#                 "edges": [
#                     {
#                         "label": ig_graph.es[i]["label"],
#                         "visible": ig_graph.es[i]["visible"]
#                     } for i in range(len(ig_graph.es))
#                 ] if ig_graph and len(ig_graph.es) > 0 else []
#             }
            
#             # 7. 生成HTML并写入字节流
#             buf = BytesIO()
            
#             # 使用StringIO捕获SVG内容
#             svg_buffer = StringIO()
#             if ig_graph:  # 确保图对象已初始化
#                 ig_graph.save(
#                     svg_buffer,
#                     format='svg',
#                     layout=layout,
#                     bbox=(1000, 800),
#                     vertex_label_size=10,
#                     edge_label_size=8,
#                     margin=50,
#                     vertex_frame_width=1,
#                     vertex_frame_color="#ffffff"
#                 )
#             svg_content = svg_buffer.getvalue()
#             svg_buffer.close()
            
#             # 生成HTML内容
#             html_content = template.replace("{{ svg_content }}", svg_content)
#             html_content = html_content.replace("{{ custom_css }}", custom_css)
#             html_content = html_content.replace("{{ graph_data }}", json.dumps(graph_data))
#             html_content = html_content.replace("{% if has_more %}", "" if has_more else "<!--")
#             html_content = html_content.replace("{% endif %}", "" if has_more else "-->")
            
#             buf.write(html_content.encode('utf-8'))
#             buf.seek(0)
            
#             return buf
            
#         except Exception as e:
#             # 异常处理，确保即使出错也能返回有效字节流
#             buf = BytesIO()
#             error_html = f"<html><body><h3>可视化生成错误: {str(e)}</h3></body></html>"
#             buf.write(error_html.encode('utf-8'))
#             buf.seek(0)
#             return buf

def generate_kg_visualization(self) -> BytesIO:
        """生成树状时间线图谱（突出用户节点，按时间树状排列）"""
        # 初始化网络，使用垂直方向树状布局
        net = Network(
            height="800px",
            width="100%",
            bgcolor="#ffffff",
            font_color="#333333",
            directed=True,
            layout=True
        )
        
        # 定义实体样式（强化用户节点突出度）
        color_map = {
            "用户": {"color": "#2c3e50", "size": 40, "shape": "circularImage"},  # 深色大节点突出
            "地点": {"color": "#3498db", "size": 20, "shape": "box"},
            "时间": {"color": "#f1c40f", "size": 18, "shape": "ellipse"},
            "导航事件": {"color": "#e74c3c", "size": 25, "shape": "diamond"}
        }
        
        # 1. 提取并排序导航事件（按时间）
        event_nodes = []
        for node, data in self.graph.nodes(data=True):
            if data.get("entity_type") == "导航事件":
                # 找到事件关联的开始时间
                for _, end_node, edge_data in self.graph.out_edges(node, data=True):
                    if edge_data.get("relation") == "开始于":
                        time_node = end_node
                        time_data = self.graph.nodes[time_node]
                        try:
                            time_str = time_data.get("label", "")
                            if '.' in time_str:
                                time_str = time_str.split('.')[0]
                            time_obj = datetime.fromisoformat(time_str)
                            event_nodes.append((node, time_obj, time_node))
                        except Exception:
                            continue
                        break
        
        # 按时间排序事件
        event_nodes.sort(key=lambda x: x[1])
        # 分配事件层级（用户为根节点，事件按时间顺序为第一级子节点）
        event_level = {node: 2 for node, _, _ in event_nodes}  # 事件在第2层
        time_mapping = {node: time_node for node, _, time_node in event_nodes}  # 事件-时间映射
        
        # 2. 添加节点（按树状层级组织）
        user_node = None
        # 先找到用户节点
        for node, data in self.graph.nodes(data=True):
            if data.get("entity_type") == "用户":
                user_node = node
                break
        
        # 添加所有节点并设置层级
        for node, data in self.graph.nodes(data=True):
            entity_type = data.get("entity_type", "未知")
            style = color_map.get(entity_type, {"color": "#95a5a6", "size": 18, "shape": "circle"})
            
            # 层级设计：
            # - 用户节点：层级1（根节点）
            # - 导航事件：层级2（按时间顺序排列）
            # - 时间/地点：层级3（事件的子节点）
            level = 1 if entity_type == "用户" else \
                    event_level.get(node, 3)  # 事件为2级，其他为3级
            
            # 为地点/时间节点设置父级（关联的事件）
            parent = None
            if entity_type in ["地点", "时间"]:
                # 找到关联的事件作为父节点
                for pred in self.graph.predecessors(node):
                    if self.graph.nodes[pred].get("entity_type") == "导航事件":
                        parent = pred
                        break
            
            net.add_node(
                node,
                label=data.get("label", node),
                color=style["color"],
                size=style["size"],
                shape=style["shape"],
                level=level,
                parent=parent,  # 树状结构的父节点关联
                title=f"{entity_type}: {data.get('label', node)}\n{json.dumps({k: v for k, v in data.items() if k not in ['label', 'entity_type']}, ensure_ascii=False)}"
            )
        
        # 3. 添加边（强化树状关系）
        for u, v, data in self.graph.edges(data=True):
            # 特殊处理用户到事件的边（主树干）
            u_type = self.graph.nodes[u].get("entity_type")
            v_type = self.graph.nodes[v].get("entity_type")
            
            # 样式区分：用户到事件的边加粗
            width = 4 if (u_type == "用户" and v_type == "导航事件") else 2
            
            net.add_edge(
                u, v,
                label=data.get("relation", ""),
                title=f"{data.get('relation', '')}" + (f"\n间隔: {data.get('avg_interval'):.1f}分钟" if "avg_interval" in data else ""),
                width=width,
                smooth={"type": "vertical", "forceDirection": "vertical"},  # 垂直方向平滑曲线
                color={"color": "#7f8c8d" if width == 2 else "#2c3e50"}  # 主树干深色
            )
        
        # 4. 树状布局配置（从上到下按时间顺序）
        # net.set_options('''
        # {
        #     "layout": {
        #         "hierarchical": {
        #             "enabled": true,
        #             "direction": "UD", 
        #             "levelSeparation": 180,  
        #             "nodeSpacing": 120,  
        #             "treeSpacing": 200, 
        #             "blockShifting": true,
        #             "edgeMinimization": true,
        #             "parentCentralization": true 
        #         }
        #     },
        #     "edges": {
        #         "shadow": false,
        #         "arrows": {
        #             "to": {
        #                 "enabled": true,
        #                 "scaleFactor": 0.8
        #             }
        #         }
        #     },
        #     "nodes": {
        #         "shadow": true,
        #         "font": {
        #             "size": 12,
        #             "color": "#2c3e50"
        #         },
        #         "borderWidth": 2
        #     },
        #     "interaction": {
        #         "hover": true,
        #         "tooltipDelay": 200,
        #         "dragNodes": true,
        #         "zoomView": true,
        #         "selectConnectedEdges": false
        #     }
        # }
        # ''')
        
        # 保存到临时文件再转为BytesIO
        try:
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html') as tmp:
                temp_filename = tmp.name
            
            net.save_graph(temp_filename)
            
            buf = BytesIO()
            with open(temp_filename, 'rb') as f:
                buf.write(f.read())
            buf.seek(0)
            
            return buf
        finally:
            if os.path.exists(temp_filename):
                os.remove(temp_filename)


if __name__ == "__main__":
    # 示例数据
    nav_data = [
        {"start_time": "2023-10-01 08:00:00", "poi": "公司", "type": "工作"},
        {"start_time": "2023-10-01 09:00:00", "poi": "餐厅", "type": "餐饮"},
        {"start_time": "2023-10-01 10:00:00", "poi": "公司", "type": "工作"},
        {"start_time": "2023-10-01 11:00:00", "poi": "咖啡厅", "type": "休闲"},
        {"start_time": "2023-10-01 12:00:00", "poi": "餐厅", "type": "餐饮"},
        {"start_time": "2023-10-01 13:00:00", "poi": "公司", "type": "工作"}]

    plot_destination_time_heatmap(nav_data)
    plt.show()
    plot_destination_type_pie(nav_data)
    plt.show()
