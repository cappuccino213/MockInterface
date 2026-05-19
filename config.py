"""
@File : config.py
@Date : 2023/7/25 13:57
@Author: 九层风（YePing Zhang）
@Contact : yeahcheung213@163.com
"""
import os

import toml
# 优先使用 tomlkit 保留注释，fallback 到标准 toml
try:
    import tomlkit
    from tomlkit import TOMLDocument
    HAS_TOMLKIT = True
except ImportError:
    HAS_TOMLKIT = False


class ConfigManager:
    def __init__(self, file_path):
        """保证config.toml和配置管理模块在同级目录，使得次级模块引入也不会报错"""
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.file_path = os.path.join(self.current_dir, file_path)
        self._config = None
        self._toml_doc = None

    def _load_config(self):
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                if HAS_TOMLKIT:
                    self._toml_doc = tomlkit.load(f)
                    self._config = self._toml_doc
                else:
                    toml_data = toml.load(f)
                    self._config = toml_data
        except FileNotFoundError:
            print(f"Error Config file {self.file_path} not found.")
        except Exception as e:
            print(f"Error loading or parsing config: {e}")

    def get_config(self):
        """获取配置数据。如果配置尚未加载，则先加载配置。"""
        if self._config is None:
            self._load_config()
        return self._config

    def update_section(self, section: str, updates: dict):
        """更新指定 section 的配置项，保留原有注释"""
        if not HAS_TOMLKIT:
            raise RuntimeError("tomlkit 未安装，无法保留注释进行写入")

        if self._toml_doc is None:
            self._load_config()

        # 确保 section 存在
        if section not in self._toml_doc:
            self._toml_doc[section] = {}

        # 更新配置
        for key, value in updates.items():
            self._toml_doc[section][key] = value

        # 写回文件
        with open(self.file_path, 'w', encoding='utf-8') as f:
            tomlkit.dump(self._toml_doc, f)

        # 重新加载
        self._load_config()


# 初始化配置管理器
config_manager = ConfigManager('config.toml')

CONFIG = config_manager.get_config()


def get_current_config():
    """
    动态获取当前配置（支持热重载）
    
    如果启用了配置热重载，则从热重载管理器获取最新配置
    否则返回静态 CONFIG
    
    Returns:
        配置字典
    """
    try:
        from config_hot_reload import get_config_hot_reload
        hot_reload = get_config_hot_reload()
        # 如果热重载已启动且正在运行，使用热重载的配置
        if hot_reload._monitor_thread and hot_reload._monitor_thread.is_alive():
            return hot_reload.get_config()
    except Exception:
        pass
    
    # 降级：返回静态配置
    return CONFIG


if __name__ == "__main__":
    print(CONFIG)
