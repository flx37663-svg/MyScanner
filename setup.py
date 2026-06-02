# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import json

def print_msg(msg, type="info"):
    colors = {"success": "\033[92m", "info": "\033[94m", "warn": "\033[93m", "error": "\033[91m"}
    reset = "\033[0m"
    print(f"{colors.get(type, '')}[*] {msg}{reset}")

def setup():
    print_msg("开始一键配置 SCANNER 扫描环境...", "info")

    # 1. 创建必要的目录结构
    dirs = ['pocs', 'reports', 'core', 'pocsuite3', 'pocsuite3/lib/core']
    for d in dirs:
        if not os.path.exists(d):
            print_msg(f"{d} 缺失！！！！请检查", "warn")
        exit()

    # 2. 安装依赖库
    packages = ['requests', 'paramiko', 'websockets']
    print_msg("正在安装 Python 依赖库...", "info")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", *packages])
        print_msg("依赖库安装成功。", "success")
    except Exception as e:
        print_msg(f"安装失败，请手动执行: pip install {' '.join(packages)}", "error")

    # 3. 初始化 config.json (如果不存在)
    config_path = "config.json"
    if not os.path.exists(config_path):
        default_config = {
            "target_url": "http://127.0.0.1",
            "threads": 5,
            "timeout": 10,
            "headers": {
                "Cookie": "",
                "User-Agent": "Mozilla/5.0 Scanner/1.0"
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
        print_msg("已生成默认配置文件 config.json", "success")
    else:
        print_msg("config.json 已存在，跳过生成。", "warn")

    # 4. 初始化 pass.txt (爆破字典)
    pass_path = "pass.txt"
    if not os.path.exists(pass_path):
        default_pass = ["admin", "123456", "password", "root", "admin123"]
        with open(pass_path, "w") as f:
            f.write("\n".join(default_pass))
        print_msg("已生成默认字典 pass.txt", "success")

    # 5. 创建 pocsuite3/__init__.py
    init_py = "pocsuite3/__init__.py"
    if not os.path.exists(init_py):
        with open(init_py, "w") as f:
            f.write("from .api import *")
        print_msg("已初始化 pocsuite3 仿真层。", "success")

    print_msg("\n环境配置完成！现在你可以将 PoC 放入 pocs 目录并运行 python main.py 了。", "success")

if __name__ == "__main__":
    setup()