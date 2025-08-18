import networkx as nx
import pandas as pd
from typing import List, Dict, Any
import json
import io  # 新增：导入io模块
from datetime import datetime
from pyvis.network import Network
from io import BytesIO, StringIO
from Handle_csv.Util import calculate_time_diff
from Handle_csv.scenario.navigation.visualization import generate_kg_visualization
import os
import tempfile

class NavigationKnowledgeGraph:
    """导航知识图谱核心类（支持预测性导航和智能提醒）"""
    
    def __init__(self, user_id: str = "default_user"):
        self.graph = nx.DiGraph()  # 有向图存储实体关系
        self.user_id = user_id
        self._add_user_entity()  # 初始化用户实体
    
    def _add_user_entity(self) -> None:
        """添加用户实体"""
        self.graph.add_node(
            f"user_{self.user_id}",
            type="user",
            label=f"用户{self.user_id}",
            entity_type="用户"  # 确保设置entity_type
        )
    
    def add_location_entity(self, location_id: str, coords: str, loc_type: str, name: str = "") -> None:
        """添加地点实体"""
        if not name:
            # name = get_location_regeo(coords) or f"未知地点({coords})"
            name = f"未知地点({coords})"
        
        self.graph.add_node(
            location_id,
            type=loc_type,
            label=name,
            coordinates=coords,
            address=name,
            entity_type="地点"  # 确保设置entity_type
        )
    
    def add_time_entity(self, time_id: str, time_str: str) -> None:
        """添加时间实体"""
        try:
            # 处理不同格式的时间字符串
            if '.' in time_str:
                time_str = time_str.split('.')[0]  # 移除毫秒部分
            time_obj = datetime.fromisoformat(time_str)
            time_attr = {
                "type": "timestamp",
                "label": time_str,
                "hour": time_obj.hour,
                "weekday": time_obj.weekday(),  # 0=周一, 6=周日
                "date": time_obj.date().isoformat(),
                "entity_type": "时间"  # 确保设置entity_type
            }
            self.graph.add_node(time_id, **time_attr)
        except Exception as e:
            print(f"时间格式错误: {time_str}, 错误: {e}")
            # 即使解析失败也添加节点，避免后续KeyError
            self.graph.add_node(
                time_id,
                type="invalid_timestamp",
                label="无效时间",
                entity_type="时间"  # 确保设置entity_type
            )
    
    def add_navigation_event(self, event_id: str, start_loc_id: str, end_loc_id: str, 
                            start_time_id: str, end_time_id: str, duration: float) -> None:
        """添加导航事件实体及关系"""
        self.graph.add_node(
            event_id,
            type="navigation",
            label=f"导航事件{event_id.split('_')[-1]}",
            duration=duration,
            entity_type="导航事件"  # 确保设置entity_type
        )
        
        # 构建关系
        self.graph.add_edge(f"user_{self.user_id}", event_id, relation="发起")
        self.graph.add_edge(event_id, start_loc_id, relation="从...出发")
        self.graph.add_edge(event_id, end_loc_id, relation="前往...")
        self.graph.add_edge(event_id, start_time_id, relation="开始于")
        self.graph.add_edge(event_id, end_time_id, relation="结束于")
    
    def add_location_relation(self, prev_loc_id: str, curr_loc_id: str, time_interval: float) -> None:
        """添加地点间的先后关系"""
        self.graph.add_edge(
            prev_loc_id,
            curr_loc_id,
            relation="后续地点",
            avg_interval=time_interval,
            weight=1.0
        )
    
    def build_from_json_info(self, json_info_list: List[Dict[str, Any]]) -> None:
        """从导航信息列表构建知识图谱"""
        if not json_info_list:
            return
        
        location_cache = {}
        prev_loc_id = None
        prev_end_time = None
        
        for i, item in enumerate(json_info_list):
            # 确保必要字段存在
            required_fields = ["start_location", "poi_location", "start_time", "end_time", "poi"]
            if not all(field in item for field in required_fields):
                print(f"跳过不完整数据: {item}")
                continue
            
            # 处理地点实体
            start_loc_id = f"loc_start_{i}"
            self.add_location_entity(
                start_loc_id,
                coords=item["start_location"],
                loc_type="start",
                name=f"起点{i}"
            )
            
            poi_loc_id = f"loc_poi_{i}"
            self.add_location_entity(
                poi_loc_id,
                coords=item["poi_location"],
                loc_type="poi",
                name=item["poi"]
            )
            
            # 处理时间实体
            start_time_id = f"time_start_{i}"
            self.add_time_entity(start_time_id, item["start_time"])
            
            end_time_id = f"time_end_{i}"
            self.add_time_entity(end_time_id, item["end_time"])
            
            # 处理导航事件
            try:
                duration = calculate_time_diff(item["start_time"], item["end_time"]) / 60
                event_id = f"event_{i}"
                self.add_navigation_event(
                    event_id,
                    start_loc_id,
                    poi_loc_id,
                    start_time_id,
                    end_time_id,
                    duration
                )
            except Exception as e:
                print(f"计算导航时长失败: {e}")
                continue
            
            # 构建地点先后关系
            if prev_loc_id and prev_end_time:
                try:
                    interval = calculate_time_diff(prev_end_time, item["start_time"]) / 60
                    self.add_location_relation(prev_loc_id, start_loc_id, interval)
                except Exception as e:
                    print(f"计算时间间隔失败: {e}")
            
            prev_loc_id = poi_loc_id
            prev_end_time = item["end_time"]
    
    def get_prediction_features(self) -> Dict[str, Any]:
        """提取预测特征（增加容错处理）"""
        loc_freq = {}
        hour_dist = {}
        transition_probs = {}
        
        # 遍历节点时增加容错处理
        for node, data in self.graph.nodes(data=True):
            # 确保entity_type存在
            entity_type = data.get("entity_type")
            if not entity_type:
                continue
                
            if entity_type == "地点":
                loc_freq[node] = len(list(self.graph.predecessors(node)))
            elif entity_type == "时间":
                hour = data.get("hour")
                if hour is not None:
                    hour_dist[hour] = hour_dist.get(hour, 0) + 1
        
        # 处理关系
        for u, v, data in self.graph.edges(data=True):
            if data.get("relation") == "后续地点":
                transition_probs[(u, v)] = transition_probs.get((u, v), 0) + data.get("weight", 1.0)
        
        return {
            "location_frequency": loc_freq,
            "hour_distribution": hour_dist,
            "transition_probabilities": transition_probs
        }
    
    # def generate_visualization(self) -> BytesIO:
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
        net.set_options('''
        {
            "layout": {
                "hierarchical": {
                    "enabled": true,
                    "direction": "UD", 
                    "levelSeparation": 180,  
                    "nodeSpacing": 120,  
                    "treeSpacing": 200, 
                    "blockShifting": true,
                    "edgeMinimization": true,
                    "parentCentralization": true 
                }
            },
            "edges": {
                "shadow": false,
                "arrows": {
                    "to": {
                        "enabled": true,
                        "scaleFactor": 0.8
                    }
                }
            },
            "nodes": {
                "shadow": true,
                "font": {
                    "size": 12,
                    "color": "#2c3e50"
                },
                "borderWidth": 2
            },
            "interaction": {
                "hover": true,
                "tooltipDelay": 200,
                "dragNodes": true,
                "zoomView": true,
                "selectConnectedEdges": false
            }
        }
        ''')
        
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
    def generate_visualization(self) -> BytesIO:
        """生成支持折叠/展开的导航图谱：超过7个导航节点自动折叠，时间地点可切换显示"""
        return generate_kg_visualization(self)
    

    def export_to_json(self, file_path: str) -> None:
        """导出图谱数据到JSON"""
        data = {
            "nodes": [{"id": n, **self.graph.nodes[n]} for n in self.graph.nodes],
            "edges": [{"source": u, "target": v,** d} for u, v, d in self.graph.edges(data=True)]
        }
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
