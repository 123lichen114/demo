# demo/utils/cache_manager.py
# 将所有print替换为logger.info
import os
import pickle
import hashlib
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional
from utils.logger_setup import setup_logger  # 新增导入

class CacheManager:
    """支持离线缓存的缓存管理器，将缓存数据持久化到本地文件"""
    
    def __init__(self):
        self.cache_dir = Path(".cache")
        self.cache_file = self.cache_dir / "offline_cache.pkl"
        self.cache_dir.mkdir(exist_ok=True)
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.logger = setup_logger()  # 初始化日志对象
        self._load_offline_cache()
    
    def _load_offline_cache(self) -> None:
        """从本地文件加载离线缓存"""
        try:
            if self.cache_file.exists() and self.cache_file.stat().st_size > 0:
                with open(self.cache_file, 'rb') as f:
                    self.cache = pickle.load(f)
                self.logger.info(f"成功加载离线缓存，包含 {len(self.cache)} 个文件缓存")  # 修改为logger
        except (pickle.UnpicklingError, EOFError, Exception) as e:
            self.logger.error(f"加载离线缓存失败: {str(e)}，将使用新缓存")  # 修改为logger
            if self.cache_file.exists():
                backup_file = self.cache_file.with_suffix(".pkl.bak")
                os.rename(self.cache_file, backup_file)
                self.logger.info(f"损坏的缓存已备份至 {backup_file}")  # 修改为logger
            self.cache = {}
    
    def _save_offline_cache(self) -> None:
        """将当前缓存保存到本地文件"""
        try:
            with open(self.cache_file, 'wb') as f:
                pickle.dump(self.cache, f)
            print(f"缓存已保存至 {self.cache_file}")
        except Exception as e:
            print(f"保存离线缓存失败: {str(e)}")
    
    def get_file_cache(self, filename: str) -> Optional[Dict[str, Any]]:
        """获取指定文件的缓存"""
        return self.cache.get(filename)
    
    def is_cache_valid(self, filename: str, df: pd.DataFrame) -> bool:
        """检查缓存是否有效（文件存在且内容一致）"""
        if filename not in self.cache:
            return False
            
        # 比较数据帧的哈希值确保内容一致
        cached_df = self.cache[filename].get('df')
        if cached_df is None:
            return False
            
        return self._df_hash(df) == self._df_hash(cached_df)
    
    def update_file_cache(self, filename: str, df: pd.DataFrame) -> None:
        """更新文件缓存（创建或覆盖）"""
        # 初始化文件缓存结构
        if filename not in self.cache:
            self.cache[filename] = {
                'df': None,
                'content_dict': {}
            }
        
        # 更新数据帧并重置内容字典（数据变化时内容需重新计算）
        self.cache[filename]['df'] = df.copy()
        self.cache[filename]['content_dict'] = {}
        
        # 保存到离线文件
        self._save_offline_cache()
    
    def get_content_cache(self, filename: str, content_key: str) -> Optional[Any]:
        """获取指定文件的指定内容缓存"""
        if filename not in self.cache:
            return None
        return self.cache[filename]['content_dict'].get(content_key)
    
    def set_content_cache(self, filename: str, content_key: str, content: Any) -> None:
        """设置指定文件的指定内容缓存"""
        if filename not in self.cache:
            return
            
        # 仅缓存可序列化的内容
        try:
            # 测试是否可序列化
            pickle.dumps(content)
            self.cache[filename]['content_dict'][content_key] = content
            # 保存到离线文件
            self._save_offline_cache()
        except Exception as e:
            print(f"内容 {content_key} 不可序列化，无法缓存: {str(e)}")
    
    def clear_cache(self, filename: Optional[str] = None) -> None:
        """清除缓存，可指定文件名（None则清除所有）"""
        if filename:
            if filename in self.cache:
                del self.cache[filename]
                print(f"已清除 {filename} 的缓存")
        else:
            self.cache = {}
            print("已清除所有缓存")
        
        # 保存到离线文件
        self._save_offline_cache()
    
    def _df_hash(self, df: pd.DataFrame) -> str:
        """计算DataFrame的哈希值，用于比较内容是否一致"""
        # 结合数据和元数据生成哈希
        df_str = str(df.shape) + df.to_csv(index=False)
        return hashlib.md5(df_str.encode()).hexdigest()

# 创建全局缓存管理器实例
cache_manager = CacheManager()
