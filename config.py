"""
@File : config.py
@Date : 2023/7/25 13:57
@Author: 九层风（YePing Zhang）
@Contact : yeahcheung213@163.com
"""
import toml


def get_config():
    with open("config.toml", "rb") as file:
        toml_data = file.read()
    data = toml.loads(toml_data.decode('utf8'))
    return data


CONFIG = get_config()
if __name__ == "__main__":
    print(get_config())
