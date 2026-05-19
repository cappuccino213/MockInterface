"""
@File : main.py
@Date : 2023/7/12 16:25
@Author: 九层风（YePing Zhang）
@Contact : yeahcheung213@163.com
"""
import os
import sys
import time
import signal
import platform

# 导入配置
from config import CONFIG

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from routers.dep_router import dep_route
from routers.token_router import token_route, product_route
from routers.archive_router import archive_route
from routers.follow_up_router import follow_up_route
from routers.imcis_router import imcis_route
from routers.exam_recognition_router import recognition_route
from routers.admin_router import admin_route

from multiprocessing import freeze_support


# ==================== 配置热重载 ====================

def init_config_hot_reload():
    """初始化配置热重载"""
    from config_hot_reload import get_config_hot_reload
    
    hot_reload = get_config_hot_reload()
    
    # 注册配置变更回调
    def on_config_changed(new_config):
        print(f"[Main] 配置已更新，当前 mockup.locale = {new_config.get('mockup', {}).get('locale', 'N/A')}")
        
        # 重新加载 FakeData 对象以应用新的 locale
        try:
            from utility import fake_data
            fake_data._reload_config()
            print(f"[Main] FakeData 已重新加载，新 locale: {new_config.get('mockup', {}).get('locale', 'N/A')}")
        except Exception as e:
            print(f"[Main] 重新加载 FakeData 失败: {e}")
    
    hot_reload.register_callback(on_config_changed)
    
    # 启动监控
    hot_reload.start()
    
    return hot_reload


# ==================== 重启过渡模式检测 ====================
# 通过环境变量检测是否是过渡模式重启
_is_transition_mode = os.environ.get('RESTART_TRANSITION') == '1'


# ==================== 重启检测 ====================
def check_restart_marker():
    """检测重启标志，让旧进程退出"""
    routers_dir = os.path.dirname(os.path.abspath(__file__))
    marker_file = os.path.join(routers_dir, 'routers', '.restart_marker')

    if os.path.exists(marker_file):
        try:
            with open(marker_file, 'r') as f:
                content = f.read().strip()
            
            # 如果内容为空，删除文件并返回
            if not content:
                os.remove(marker_file)
                return None
            
            # 解析格式: old_pid|real_port
            parts = content.split('|')
            if len(parts) < 1 or not parts[0].isdigit():
                os.remove(marker_file)
                return None
            
            old_pid = int(parts[0])
            real_port = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else CONFIG['uvicorn']['port']

            # 当前进程是旧进程，需要退出
            if old_pid == os.getpid():
                print(f"[Main] 当前是旧进程 ({old_pid})，即将退出让新进程接管...")
                os.remove(marker_file)
                sys.exit(0)

            # 当前进程是新进程（过渡模式），需要让旧进程退出
            if _is_transition_mode:
                print(f"[Main] 检测到重启信号，通知旧进程 ({old_pid}) 退出...")
                try:
                    os.kill(old_pid, signal.SIGTERM)
                except (ProcessLookupError, PermissionError, OSError):
                    pass  # 进程已退出或权限不足
                
                # 等待旧进程退出
                for _ in range(20):  # 最多等待10秒
                    try:
                        os.kill(old_pid, 0)  # 检查进程是否存在
                        time.sleep(0.5)
                    except OSError:
                        break
                
                # Windows 上强制终止使用 taskkill
                if platform.system() == 'Windows':
                    os.system(f'taskkill /PID {old_pid} /F')
                else:
                    # Unix 系统
                    try:
                        os.kill(old_pid, 9)  # SIGKILL
                    except OSError:
                        pass
                
                time.sleep(1)
                print(f"[Main] 旧进程已退出，使用真实端口 {real_port} 重新启动...")
                os.remove(marker_file)
                return real_port  # 返回真实端口，让调用者重启
            else:
                # 正常启动模式，清理标记文件
                try:
                    os.kill(old_pid, signal.SIGTERM)
                except:
                    pass
                os.remove(marker_file)
        except Exception:
            pass
    return None


restart_real_port = check_restart_marker()

app = FastAPI()

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 注册路由
app.include_router(archive_route)
app.include_router(follow_up_route)
app.include_router(imcis_route)
app.include_router(token_route)
app.include_router(product_route)
app.include_router(dep_route)
app.include_router(recognition_route)

# 管理后台路由
app.include_router(admin_route)

if __name__ == "__main__":
    # uvicorn.run(app='main:app', host='0.0.0.0', port=8888, reload=True)
    freeze_support()  # 解决pyinstaller打包后无限重启的问题
    
    # 如果是过渡模式重启，需要用真实端口重新启动
    if restart_real_port is not None:
        actual_port = restart_real_port
    else:
        actual_port = CONFIG['uvicorn']['port']

    # 配置日志文件输出
    log_config = CONFIG.get('logging', {})
    enable_file = log_config.get('enable_file', False)
    log_level = log_config.get('level', 'info').upper()
    
    if enable_file:
        log_dir = log_config.get('log_dir', 'logs')
        log_file = log_config.get('log_file', 'app.log')
        
        project_dir = os.path.dirname(os.path.abspath(__file__))
        log_dir_path = os.path.join(project_dir, log_dir)
        if not os.path.exists(log_dir_path):
            os.makedirs(log_dir_path)
        log_path = os.path.join(log_dir_path, log_file)
        
        # uvicorn 日志配置：同时输出到控制台和文件
        log_config_dict = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {"format": "%(asctime)s - %(levelname)s - %(message)s"},
            },
            "handlers": {
                "console": {"class": "logging.StreamHandler", "formatter": "default"},
                "file": {
                    "class": "logging.FileHandler",
                    "filename": log_path,
                    "encoding": "utf-8",
                    "formatter": "default"
                }
            },
            "root": {"level": log_level, "handlers": ["console", "file"]}
        }
    else:
        log_config_dict = None  # 使用 uvicorn 默认日志配置

    # 启动配置热重载（仅在不使用 Uvicorn reload 时启用）
    use_uvicorn_reload = CONFIG['uvicorn']['reload']
    if not use_uvicorn_reload:
        print("[Main] 启动配置热重载管理器...")
        hot_reload_manager = init_config_hot_reload()
    else:
        print("[Main] Uvicorn reload 已启用，跳过配置热重载（建议生产环境关闭 reload）")
        hot_reload_manager = None

    # Nuitka 打包后不能使用字符串形式的 app 导入，直接传递 app 对象
    uvicorn.run(
        app="main:app",
        host='0.0.0.0',
        port=actual_port,
        reload=use_uvicorn_reload,
        workers=CONFIG['uvicorn']['process_num'],
        log_config=log_config_dict
    )
