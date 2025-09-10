"""
@File : config.py
@Date : 2023/7/25 13:57
@Author: 九层风（YePing Zhang）
@Contact : yeahcheung213@163.com
"""
import os

import toml


# def get_config():
#     with open("config.toml", "rb") as file:
#         toml_data = file.read()
#     data = toml.loads(toml_data.decode('utf8'))
#     return data
#
#
# CONFIG = get_config()

# 优化解析配置文件方法
class ConfigManager:
    def __init__(self, file_path):
        """保证config.toml和配置管理模块在同级目录，使得次级模块引入也不会报错"""
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.file_path = os.path.join(self.current_dir, file_path)
        self._config = None

    def _load_config(self):
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
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


# 初始化配置管理器
config_manager = ConfigManager('config.toml')

CONFIG = config_manager.get_config()


if __name__ == "__main__":
    print(CONFIG)
