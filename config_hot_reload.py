"""
@File : config_hot_reload.py
@Date : 2024/1/15
@Author: AI Assistant
@Desc : 配置文件热重载管理器 - 支持运行时动态更新配置
"""
import os
import time
import threading
from typing import Callable, Dict, Any
from config import ConfigManager


class ConfigHotReload:
    """配置热重载管理器"""
    
    def __init__(self, config_file='config.toml', check_interval=2):
        """
        初始化配置热重载管理器
        
        Args:
            config_file: 配置文件路径
            check_interval: 检查间隔（秒）
        """
        self.config_file = config_file
        self.check_interval = check_interval
        self.config_manager = ConfigManager(config_file)
        
        # 文件修改时间戳
        self._last_modified = self._get_file_mtime()
        
        # 配置变更回调函数列表
        self._callbacks: list[Callable[[Dict[str, Any]], None]] = []
        
        # 线程控制
        self._monitor_thread = None
        self._stop_event = threading.Event()
        
        # 线程锁 - 保证配置读取的线程安全
        self._config_lock = threading.RLock()
        
        # 当前配置缓存
        self._current_config = None
    
    def _get_file_mtime(self) -> float:
        """获取文件最后修改时间"""
        try:
            return os.path.getmtime(self.config_file)
        except FileNotFoundError:
            return 0
    
    def start(self):
        """启动配置监控线程"""
        if self._monitor_thread and self._monitor_thread.is_alive():
            print("[ConfigHotReload] 监控线程已在运行")
            return
        
        # 加载初始配置
        with self._config_lock:
            self._current_config = self.config_manager.get_config()
        
        self._stop_event.clear()
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True,
            name="ConfigHotReload-Monitor"
        )
        self._monitor_thread.start()
        print(f"[ConfigHotReload] 配置监控已启动，检查间隔: {self.check_interval}秒")
    
    def stop(self):
        """停止配置监控"""
        if self._monitor_thread:
            self._stop_event.set()
            self._monitor_thread.join(timeout=5)
            print("[ConfigHotReload] 配置监控已停止")
    
    def _monitor_loop(self):
        """监控循环 - 在后台线程中运行"""
        print(f"[ConfigHotReload] 开始监控配置文件: {self.config_file}")
        
        while not self._stop_event.is_set():
            try:
                current_mtime = self._get_file_mtime()
                
                # 检测文件是否被修改
                if current_mtime > self._last_modified:
                    print(f"[ConfigHotReload] 检测到配置文件变化，正在重新加载...")
                    
                    # 重新加载配置
                    with self._config_lock:
                        try:
                            import copy
                            # 保存旧配置的深拷贝，避免引用问题
                            old_config = copy.deepcopy(self._current_config) if self._current_config else None
                            
                            # 强制重新加载
                            self.config_manager._load_config()
                            new_config = self.config_manager.get_config()
                            self._current_config = new_config
                            self._last_modified = current_mtime
                            
                            print(f"[ConfigHotReload] 配置重新加载成功")
                            
                            # 通知所有回调函数，传递旧配置和新配置
                            for callback in self._callbacks:
                                try:
                                    callback(old_config, new_config)
                                except Exception as e:
                                    print(f"[ConfigHotReload] 回调函数执行失败: {e}")
                        
                        except Exception as e:
                            print(f"[ConfigHotReload] 配置加载失败: {e}")
                
                # 等待下一个检查周期
                self._stop_event.wait(self.check_interval)
            
            except Exception as e:
                print(f"[ConfigHotReload] 监控循环异常: {e}")
                self._stop_event.wait(self.check_interval)
    
    def get_config(self) -> Dict[str, Any]:
        """
        获取当前配置（线程安全）
        
        Returns:
            配置字典
        """
        with self._config_lock:
            if self._current_config is None:
                # 如果还没有加载配置，先加载
                self._current_config = self.config_manager.get_config()
            return self._current_config
    
    def register_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """
        注册配置变更回调函数
        
        Args:
            callback: 回调函数，接收新配置作为参数
        """
        self._callbacks.append(callback)
        print(f"[ConfigHotReload] 已注册配置变更回调，当前回调数: {len(self._callbacks)}")
    
    def unregister_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """注销配置变更回调函数"""
        if callback in self._callbacks:
            self._callbacks.remove(callback)


# 全局单例
_config_hot_reload = None


def get_config_hot_reload() -> ConfigHotReload:
    """获取配置热重载管理器单例"""
    global _config_hot_reload
    if _config_hot_reload is None:
        _config_hot_reload = ConfigHotReload()
    return _config_hot_reload
