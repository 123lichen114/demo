import networkx as nx
import pandas as pd
from typing import List, Dict, Any
import json
from datetime import datetime
from pyvis.network import Network
from io import BytesIO, StringIO
from Handle_csv.scenario.navigation.navigation_info import get_navigation_info
from Handle_csv.Util import calculate_time_diff
from use_GaoDe_api.geo import get_location_regeo  # 用于获取地址描述
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
    
    def generate_visualization(self) -> BytesIO:
        """生成交互式图谱可视化（修复BytesIO保存问题）"""
        net = Network(
            height="600px",
            width="100%",
            bgcolor="#f8f9fa",
            font_color="black",
            directed=True
        )
        
        color_map = {
            "用户": "#4285f4",
            "地点": "#34a853",
            "时间": "#fbbc05",
            "导航事件": "#ea4335"
        }
        
        for node, data in self.graph.nodes(data=True):
            # 使用get方法避免KeyError
            entity_type = data.get("entity_type", "未知")
            net.add_node(
                node,
                label=data.get("label", node),
                color=color_map.get(entity_type, "#80868b"),
                title=f"{entity_type}: {data.get('label', node)}\n{json.dumps({k: v for k, v in data.items() if k not in ['label', 'entity_type']}, ensure_ascii=False)}"
            )
        
        for u, v, data in self.graph.edges(data=True):
            net.add_edge(
                u, v,
                label=data.get("relation", ""),
                title=f"{data.get('relation', '')}" + (f"\n间隔: {data.get('avg_interval'):.1f}分钟" if "avg_interval" in data else "")
            )
        
        # 修复：使用临时文件中转
        try:
            # 创建临时文件
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html') as tmp:
                temp_filename = tmp.name
            
            # 保存到临时文件
            net.save_graph(temp_filename)
            
            # 读取临时文件内容到BytesIO
            buf = BytesIO()
            with open(temp_filename, 'rb') as f:
                buf.write(f.read())
            buf.seek(0)
            
            return buf
        finally:
            # 确保临时文件被删除
            if os.path.exists(temp_filename):
                os.remove(temp_filename)

    def export_to_json(self, file_path: str) -> None:
        """导出图谱数据到JSON"""
        data = {
            "nodes": [{"id": n, **self.graph.nodes[n]} for n in self.graph.nodes],
            "edges": [{"source": u, "target": v,** d} for u, v, d in self.graph.edges(data=True)]
        }
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
