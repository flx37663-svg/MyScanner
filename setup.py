# -*- coding: utf-8 -*-
import os, sys, subprocess


def setup():
    print("[*] 正在初始化 MyScanner 扫描环境...")
    dirs = ['pocs', 'reports', 'core', 'pocsuite3', 'pocsuite3/lib', 'pocsuite3/lib/core']
    for d in dirs:
        if not os.path.exists(d): os.makedirs(d)

    init_file = "pocsuite3/__init__.py"
    if not os.path.exists(init_file):
        with open(init_file, "w") as f: f.write("from .api import *")

    packages = ['requests', 'paramiko', 'websockets']
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", *packages])
        print("[+] 依赖安装成功。")
    except:
        print("[!] 依赖安装失败，请手动执行 pip install。")
    print("[ OK ] 环境初始化完成。")


if __name__ == "__main__":
    setup()