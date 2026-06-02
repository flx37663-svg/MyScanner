# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import json

def print_msg(msg, type="info"):
    """ 格式化输出消息 """
    colors = {
        "success": "\033[92m",
        "info": "\033[94m",
        "warn": "\033[93m",
        "error": "\033[91m"
    }
    reset = "\033[0m"
    prefix = {"success": "[+]", "info": "[*]", "warn": "[!]", "error": "[X]"}
    print(f"{colors.get(type, '')}{prefix.get(type, '[*]')} {msg}{reset}")

def setup():
    print_msg("开始初始化 MyScanner 扫描环境...", "info")

    # 1. 创建必要的目录结构
    required_dirs = [
        'pocs',
        'reports',
        'core',
        'pocsuite3',
        'pocsuite3/lib',
        'pocsuite3/lib/core'
    ]
    for d in required_dirs:
        if not os.path.exists(d):
            os.makedirs(d)
            print_msg(f"已创建目录: {d}", "success")

    # 2. 安装依赖库 (从 requirements.txt 读取)
    if os.path.exists("requirements.txt"):
        print_msg("检测到 requirements.txt，正在安装依赖...", "info")
        try:
            # 使用当前 Python 解释器运行 pip
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print_msg("依赖库安装成功。", "success")
        except Exception as e:
            print_msg(f"依赖安装失败: {e}", "error")
    else:
        print_msg("未找到 requirements.txt，请手动确认依赖已安装。", "warn")

    # 3. 初始化默认配置文件 config.json
    config_path = "config.json"
    if not os.path.exists(config_path):
        default_config = {
            "target_url": "http://127.0.0.1",
            "threads": 5,
            "timeout": 10,
            "headers": {
                "Cookie": "PHPSESSID=your_id_here; security=low",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Scanner/1.0"
            },
            "scan_settings": {
                "target_mode": "crawler",
                "poc_mode": "all",
                "max_depth": 3,
                "max_pages": 100
            },
            "report_settings": {
                "output_dir": "./reports",
                "filename": ""
            },
            "webhook": {
                "enabled": False,
                "sendkey": ""
            }
        }
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=4)
        print_msg("已生成默认配置文件 config.json (请手动修改认证信息)", "success")
    else:
        print_msg("config.json 已存在，跳过生成。", "warn")


    # 仿真层初始化
    init_py = "pocsuite3/__init__.py"
    if not os.path.exists(init_py):
        with open(init_py, "w") as f:
            f.write("from .api import *")
        print_msg("已初始化 pocsuite3 仿真层接口。", "success")

    print_msg("\n[ OK ] MyScanner 环境配置完成！", "success")
    print_msg("提示: 运行前请确保 config.json 中的 Cookie 是最新的。", "info")

if __name__ == "__main__":
    setup()