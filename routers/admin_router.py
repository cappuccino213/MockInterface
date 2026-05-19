"""
@File : admin_router.py
@Date : 2024/1/15
@Author: AI Assistant
@Desc : 管理后台路由 - 配置管理、登录认证、服务重启
"""
import os
import sys
import secrets
import platform
import hashlib
import time
from typing import Optional

from fastapi import APIRouter, Request, Form, HTTPException, Header
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from config import ConfigManager

# ==================== 密码管理 ====================

def get_admin_password() -> str:
    """获取管理后台密码，优先级：环境变量 > .admin_password 文件 > 自动生成"""
    env_password = os.environ.get('ADMIN_PASSWORD')
    if env_password:
        return env_password

    password_file = os.path.join(os.path.dirname(__file__), '.admin_password')
    if os.path.exists(password_file):
        with open(password_file, 'r', encoding='utf-8') as f:
            return f.read().strip()

    # 首次生成随机密码
    new_password = secrets.token_urlsafe(16)
    with open(password_file, 'w', encoding='utf-8') as f:
        f.write(new_password)
    print(f"\n[Admin] 首次运行，已生成管理后台密码: {new_password}\n")
    return new_password


def verify_password(password: str) -> bool:
    """验证密码"""
    return password == get_admin_password()


# ==================== Token 认证管理 ====================

# 简单内存存储 token（打包后可正常工作）
_valid_tokens = {}  # token -> expire_time


# ==================== 重启状态管理 ====================

_restart_status = {
    "is_restarting": False,
    "restart_time": None,
    "message": ""
}


def generate_token() -> str:
    """生成认证 token"""
    token = secrets.token_urlsafe(32)
    _valid_tokens[token] = time.time() + 3600  # 1小时后过期
    return token


def verify_token(token: str) -> bool:
    """验证 token 是否有效"""
    if token not in _valid_tokens:
        return False
    if time.time() > _valid_tokens[token]:
        del _valid_tokens[token]
        return False
    return True


def get_token_from_header(authorization: Optional[str] = Header(None)) -> Optional[str]:
    """从 Authorization header 获取 token"""
    if authorization and authorization.startswith('Bearer '):
        return authorization[7:]
    return None


# ==================== TOML 配置管理 ====================

def get_toml_manager():
    """获取 TOML 配置管理器"""
    return ConfigManager('config.toml')


def to_plain_dict(obj):
    """将 tomlkit 对象转换为普通 Python 字典/列表"""
    import tomlkit
    
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


def get_config_sections():
    """获取配置文件的 sections（排除 admin 自身）"""
    config = get_toml_manager().get_config()
    config = to_plain_dict(config)  # 转换为普通字典
    admin_sections = ['admin']
    return [str(k) for k in config.keys() if k not in admin_sections]


def get_field_options():
    """获取字段选项配置（如 locale 下拉选项）"""
    config = get_toml_manager().get_config()
    config = to_plain_dict(config)  # 转换为普通字典
    field_options = config.get('admin', {}).get('field_options', {})
    return field_options


def flatten_dict(d, parent_key=''):
    """将嵌套 dict 展平为扁平的 key（用 . 连接）"""
    d = to_plain_dict(d)  # 确保是普通字典
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}.{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key).items())
        else:
            items.append((new_key, v))
    return dict(items)


def unflatten_dict(d):
    """将扁平的 key（如 year.start）转换回嵌套 dict"""
    result = {}
    for key, value in d.items():
        parts = key.split('.')
        current = result
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[parts[-1]] = value
    return result


def parse_value_type(value):
    """解析值类型并返回格式化的值"""
    # 先转换为普通 Python 对象
    value = to_plain_dict(value)
    if isinstance(value, bool):
        return {'type': 'bool', 'value': value}
    elif isinstance(value, int):
        return {'type': 'int', 'value': value}
    elif isinstance(value, float):
        return {'type': 'float', 'value': value}
    elif isinstance(value, list):
        return {'type': 'array', 'value': value}
    else:
        return {'type': 'string', 'value': str(value)}


# ==================== 路由定义 ====================

admin_route = APIRouter(prefix="/admin", tags=["Admin"])

# 初始化 Jinja2Templates
from starlette.templating import Jinja2Templates
templates = Jinja2Templates(directory="templates")

# 完全禁用 Jinja2 缓存 - 使用 None 作为缓存
class NoCache:
    """无操作缓存类"""
    def get(self, key):
        return None
    def set(self, key, value):
        pass
    def delete(self, key):
        pass
    def clear(self):
        pass
    def __contains__(self, key):
        return False
    def __getitem__(self, key):
        raise KeyError(key)
    def __setitem__(self, key, value):
        pass
    def __delitem__(self, key):
        raise KeyError(key)

templates.env.cache = NoCache()


# 登录页面
@admin_route.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """登录页面"""
    # 模板中使用 request 对象
    return templates.TemplateResponse(request=request, name="admin/login.html", context={})


# 登录提交 - 返回 token
@admin_route.post("/login")
async def login(password: str = Form(...)):
    """处理登录，返回 token"""
    if verify_password(password):
        token = generate_token()
        return {"success": True, "token": token}
    return {"success": False, "error": "密码错误"}


# 主管理页面
@admin_route.get("/", response_class=HTMLResponse)
async def admin_index(request: Request):
    """管理后台首页 - 始终返回配置页面，由前端 JS 检查 token"""
    sections = get_config_sections()
    
    # 确保所有数据都是普通 Python 类型，避免 Jinja2 缓存键错误
    sections_list = [str(s) for s in sections]
    active = str(sections[0]) if sections else None
    
    return templates.TemplateResponse(request=request, name="admin/config.html", context={
        "sections": sections_list,
        "active_section": active
    })


# 获取配置数据（JSON API）
@admin_route.get("/api/config")
async def get_config(authorization: Optional[str] = Header(None)):
    """获取配置数据"""
    token = get_token_from_header(authorization)
    if not token or not verify_token(token):
        raise HTTPException(status_code=401, detail="未登录")

    manager = get_toml_manager()
    config_data = to_plain_dict(manager.get_config())  # 转换为普通字典

    result = {}
    for section in config_data.keys():
        if section == 'admin':
            continue
        flat_data = flatten_dict(config_data[section])
        result[section] = {}
        for key, value in flat_data.items():
            result[section][key] = parse_value_type(value)

    return result


# 获取字段选项（如下拉选项）
@admin_route.get("/api/field-options")
async def get_field_options_api(authorization: Optional[str] = Header(None)):
    """获取字段选项配置"""
    token = get_token_from_header(authorization)
    if not token or not verify_token(token):
        raise HTTPException(status_code=401, detail="未登录")

    return get_field_options()


# 保存配置
@admin_route.post("/api/config/{section}")
async def save_config(section: str, config_data: dict, authorization: Optional[str] = Header(None)):
    """保存指定 section 的配置"""
    token = get_token_from_header(authorization)
    if not token or not verify_token(token):
        raise HTTPException(status_code=401, detail="未登录")

    manager = get_toml_manager()

    try:
        nested_data = unflatten_dict(config_data)
        manager.update_section(section, nested_data)
        return {"success": True, "message": f"{section} 配置已保存"}
    except Exception as e:
        return {"success": False, "message": str(e)}


# 重启服务（可选 - 如果使用配置热重载，此接口可保留用于真正需要重启的场景）
@admin_route.post("/api/restart")
async def restart_service(authorization: Optional[str] = Header(None)):
    """
    重启服务 - 仅在必要时使用
    注意：大部分配置修改已通过热重载生效，无需重启
    """
    token = get_token_from_header(authorization)
    if not token or not verify_token(token):
        raise HTTPException(status_code=401, detail="未登录")

    try:
        import subprocess
        import socket
        import threading

        # 设置重启状态
        _restart_status["is_restarting"] = True
        _restart_status["restart_time"] = time.time()
        _restart_status["message"] = "服务正在重启..."

        def delayed_restart():
            """延迟执行重启，给前端足够时间接收响应"""
            time.sleep(2)  # 延迟 2 秒，确保前端已收到响应
            
            current_pid = os.getpid()
            restart_marker = os.path.join(os.path.dirname(__file__), '.restart_marker')
            config = get_toml_manager().get_config()
            real_port = to_plain_dict(config).get('uvicorn', {}).get('port', 8888)

            # 写入重启标记
            with open(restart_marker, 'w') as f:
                f.write(f"{current_pid}|{real_port}")

            if getattr(sys, 'frozen', False):
                exe_path = sys.executable
                cmd = [exe_path, '--transition-port', '0']
            else:
                python_path = sys.executable
                main_path = os.path.abspath('main.py')
                cmd = [python_path, main_path, '--transition-port', '0']

            print("\n[Restart] 正在启动新进程...")

            if platform.system() == 'Windows':
                # Windows: 使用 DETACHED_PROCESS 让新进程独立运行
                DETACHED_PROCESS = 0x00000008
                subprocess.Popen(
                    cmd,
                    creationflags=DETACHED_PROCESS,
                    cwd=os.getcwd(),
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            else:
                # Unix/Linux/Mac: 使用 start_new_session
                subprocess.Popen(
                    cmd,
                    start_new_session=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )

            print("[Restart] 新进程已启动，当前进程即将退出...")

        # 在后台线程中执行延迟重启
        thread = threading.Thread(target=delayed_restart, daemon=True)
        thread.start()

        # 立即返回成功响应
        return {"success": True, "message": "服务将在 2 秒后重启，请稍候..."}
    except Exception as e:
        _restart_status["is_restarting"] = False
        _restart_status["message"] = ""
        return {"success": False, "message": f"重启失败: {str(e)}"}


# 新增：获取热重载状态
@admin_route.get("/api/hot-reload/status")
async def get_hot_reload_status(authorization: Optional[str] = Header(None)):
    """获取配置热重载状态"""
    token = get_token_from_header(authorization)
    if not token or not verify_token(token):
        raise HTTPException(status_code=401, detail="未登录")
    
    try:
        from config_hot_reload import get_config_hot_reload
        hot_reload = get_config_hot_reload()
        
        is_running = hot_reload._monitor_thread is not None and hot_reload._monitor_thread.is_alive()
        
        return {
            "success": True,
            "enabled": is_running,
            "check_interval": hot_reload.check_interval,
            "last_modified": hot_reload._last_modified,
            "message": "配置热重载已启用" if is_running else "配置热重载未启用"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# 获取日志
@admin_route.get("/api/logs")
async def get_logs(
    lines: int = 100,
    authorization: Optional[str] = Header(None)
):
    """获取日志内容"""
    token = get_token_from_header(authorization)
    if not token or not verify_token(token):
        raise HTTPException(status_code=401, detail="未登录")

    try:
        config = get_toml_manager().get_config()
        config = to_plain_dict(config)
        log_config = config.get('logging', {})
        
        log_dir = log_config.get('log_dir', 'logs')
        log_file = log_config.get('log_file', 'app.log')
        
        # 获取日志文件路径
        if getattr(sys, 'frozen', False):
            # exe 模式下，日志在 exe 同目录
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        log_path = os.path.join(base_dir, log_dir, log_file)
        
        if not os.path.exists(log_path):
            return {"success": True, "logs": "", "total_lines": 0}
        
        # 读取日志文件
        with open(log_path, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
        
        total_lines = len(all_lines)
        # 返回最后指定行数
        logs = ''.join(all_lines[-lines:])
        
        return {
            "success": True,
            "logs": logs,
            "total_lines": total_lines,
            "displayed_lines": min(lines, total_lines)
        }
    except Exception as e:
        return {"success": False, "logs": "", "error": str(e)}


# 获取日志文件信息
@admin_route.get("/api/logs/info")
async def get_log_info(authorization: Optional[str] = Header(None)):
    """获取日志文件信息"""
    token = get_token_from_header(authorization)
    if not token or not verify_token(token):
        raise HTTPException(status_code=401, detail="未登录")

    try:
        config = get_toml_manager().get_config()
        config = to_plain_dict(config)
        log_config = config.get('logging', {})
        
        log_dir = log_config.get('log_dir', 'logs')
        log_file = log_config.get('log_file', 'app.log')
        
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        log_path = os.path.join(base_dir, log_dir, log_file)
        
        if os.path.exists(log_path):
            stat = os.stat(log_path)
            return {
                "success": True,
                "exists": True,
                "path": log_path,
                "size": stat.st_size,
                "size_formatted": format_size(stat.st_size),
                "modified": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stat.st_mtime))
            }
        else:
            return {
                "success": True,
                "exists": False,
                "path": log_path
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


def format_size(size):
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} TB"
