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
import logging

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

# 配置日志
logger = logging.getLogger(__name__)


# ==================== 配置热重载 ====================

def init_config_hot_reload():
    """初始化配置热重载"""
    from config_hot_reload import get_config_hot_reload
    
    hot_reload = get_config_hot_reload()
    
    def flatten_dict(d, parent_key='', sep='.'):
        """将嵌套字典展平为单层字典"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(flatten_dict(v, new_key, sep=sep).items())
            else:
                # 将值转换为基本类型，避免 tomlkit 特殊类型导致比较失败
                if hasattr(v, 'value'):
                    v = v.value
                items.append((new_key, v))
        return dict(items)
    
    def to_plain_dict(obj):
        """将 tomlkit 对象转换为普通 Python 字典/列表"""
        try:
            import tomlkit
        except ImportError:
            return obj
        
        # 基本类型直接返回
        if obj is None or isinstance(obj, (str, int, float, bool)):
            return obj
        
        # 处理 tomlkit 的特殊类型
        if isinstance(obj, tomlkit.TOMLDocument):
            return {str(k): to_plain_dict(v) for k, v in obj.items()}
        if isinstance(obj, tomlkit.items.Table):
            return {str(k): to_plain_dict(v) for k, v in obj.items()}
        if isinstance(obj, tomlkit.items.InlineTable):
            return {str(k): to_plain_dict(v) for k, v in obj.items()}
        if isinstance(obj, tomlkit.items.Array):
            return [to_plain_dict(item) for item in obj]
        if isinstance(obj, tomlkit.items.String):
            return str(obj)
        if isinstance(obj, tomlkit.items.Integer):
            return int(obj)
        if isinstance(obj, tomlkit.items.Float):
            return float(obj)
        if isinstance(obj, tomlkit.items.Bool):
            return bool(obj)
        
        # 处理标准 Python 类型
        if isinstance(obj, dict):
            return {str(k): to_plain_dict(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [to_plain_dict(item) for item in obj]
        
        # 其他类型转为字符串
        return str(obj)
    
    def compare_configs(old_config, new_config):
        """对比两个配置，返回变更项"""
        if old_config is None:
            return {"added": list(new_config.keys()), "modified": [], "removed": []}
        
        # 先转换为普通字典，避免 tomlkit 类型问题
        old_plain = to_plain_dict(old_config)
        new_plain = to_plain_dict(new_config)
        
        old_flat = flatten_dict(old_plain)
        new_flat = flatten_dict(new_plain)
        
        added = []
        modified = []
        removed = []
        
        # 检查新增和修改的键
        for key, new_value in new_flat.items():
            if key not in old_flat:
                added.append(key)
            elif old_flat[key] != new_value:
                modified.append({
                    'key': key,
                    'old_value': old_flat[key],
                    'new_value': new_value
                })
        
        # 检查删除的键
        for key in old_flat:
            if key not in new_flat:
                removed.append(key)
        
        return {
            'added': added,
            'modified': modified,
            'removed': removed
        }
    
    # 注册配置变更回调
    def on_config_changed(old_config, new_config):
        # 对比配置变更
        changes = compare_configs(old_config, new_config)
        
        logger.info("\n" + "="*60)
        logger.info("[Main] 配置已保存")
        logger.info("="*60)
        
        # 打印新增的配置项
        if changes['added']:
            logger.info(f"\n📝 新增配置项 ({len(changes['added'])} 项):")
            for key in changes['added']:
                new_value = to_plain_dict(new_config)
                for k in key.split('.'):
                    if isinstance(new_value, dict):
                        new_value = new_value.get(k, 'N/A')
                    else:
                        new_value = 'N/A'
                        break
                logger.info(f"  + {key} = {new_value}")
        
        # 打印修改的配置项
        if changes['modified']:
            logger.info(f"\n[edit]  修改配置项 ({len(changes['modified'])} 项):")
            for change in changes['modified']:
                logger.info(f"  ~ {change['key']}")
                logger.info(f"    旧值: {change['old_value']}")
                logger.info(f"    新值: {change['new_value']}")
        
        # 打印删除的配置项
        if changes['removed']:
            logger.warning(f"\n[x] 删除配置项 ({len(changes['removed'])} 项):")
            for key in changes['removed']:
                logger.warning(f"  - {key}")
        
        if not changes['added'] and not changes['modified'] and not changes['removed']:
            logger.warning("\n[warning] 未检测到配置变更")
        
        logger.info("="*60 + "\n")
        
        # 重新加载 FakeData 对象以应用新的 locale（如果 mockup.locale 发生变化）
        try:
            from utility import fake_data
            # 检查 mockup.locale 是否变化
            old_locale = None
            new_locale = None
            if old_config:
                old_plain = to_plain_dict(old_config)
                old_locale = old_plain.get('mockup', {}).get('locale')
            new_plain = to_plain_dict(new_config)
            new_locale = new_plain.get('mockup', {}).get('locale')
            
            if old_locale != new_locale:
                fake_data._reload_config()
                logger.info(f"[Main] ✅ FakeData 已重新加载，locale: {old_locale} → {new_locale}")
        except Exception as e:
            logger.error(f"[Main] ⚠️  重新加载 FakeData 失败: {e}", exc_info=True)
    
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
                logger.info(f"[Main] 当前是旧进程 ({old_pid})，即将退出让新进程接管...")
                os.remove(marker_file)
                sys.exit(0)

            # 当前进程是新进程（过渡模式），需要让旧进程退出
            if _is_transition_mode:
                logger.info(f"[Main] 检测到重启信号，通知旧进程 ({old_pid}) 退出...")
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
                logger.info(f"[Main] 旧进程已退出，使用真实端口 {real_port} 重新启动...")
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
app.mount("/static", StaticFiles(directory="./static"), name="static")

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
    log_level = str(log_config.get('level', 'info')).upper()
    
    if enable_file:
        log_dir = str(log_config.get('log_dir', 'logs'))
        log_file = str(log_config.get('log_file', 'app.log'))
        
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
        logger.info("[Main] 启动配置热重载管理器...")
        hot_reload_manager = init_config_hot_reload()
    else:
        logger.info("[Main] Uvicorn reload 已启用，跳过配置热重载（建议生产环境关闭 reload）")
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
