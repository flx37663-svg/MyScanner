# -*- coding: utf-8 -*-
import argparse
import sys
import os
from core.engine import start_engine


def banner():
    print(r"""
    __  ___      _____                                 
   /  |/  /_  __/ ___/_________ _____  ____  ___  _____
  / /|_/ / / / /\__ \/ ___/ __ `/ __ \/ __ \/ _ \/ ___/
 / /  / / /_/ /___/ / /__/ /_/ / / / / / / /  __/ /    
/_/  /_/\__, //____/\___/\__,_/_/ /_/_/ /_/\___/_/     
       /____/                                          
    """)
    print(" [ MyScanner ] - Advanced Automated Vulnerability Scanner")
    print(" GitHub: https://github.com/yourname/MyScanner\n")


def main():
    banner()
    parser = argparse.ArgumentParser(description="MyScanner: A modular automated web scanner.")

    # --- 目标设置 ---
    target_group = parser.add_argument_group('Target Settings')
    target_group.add_argument("-u", "--url", help="Target URL (e.g. http://example.com)")
    target_group.add_argument("--single", action="store_true", help="Scan only the entry URL, skip crawler")

    # --- PoC 控制 ---
    poc_group = parser.add_argument_group('PoC Controls')
    poc_group.add_argument("--poc", help="Run a single PoC file (e.g. sqli.py)")
    poc_group.add_argument("--group", help="Run a specific PoC group directory (e.g. generic)")

    # --- 性能与深度 ---
    run_group = parser.add_argument_group('Performance & Depth')
    run_group.add_argument("-t", "--threads", type=int, help="Max thread count (default: read from config)")
    run_group.add_argument("--depth", type=int, help="Max crawler depth (0 for unlimited)")
    run_group.add_argument("--pages", type=int, help="Max crawler pages")

    # --- 输出与通知 ---
    out_group = parser.add_argument_group('Output & Notify')
    out_group.add_argument("-o", "--output", help="Custom report filename (e.g. my_result.html)")
    out_group.add_argument("--no-push", action="store_true", help="Disable Webhook push for this run")

    args = parser.parse_args()

    # 简单的参数冲突检查
    if not args.url:
        # 如果没有传 -u，则之后会尝试从 config.json 读取
        pass

    try:
        # 将解析后的参数对象传递给引擎
        start_engine(args)
    except KeyboardInterrupt:
        print("\n\033[93m[!] 用户强制停止扫描 (Ctrl+C).\033[0m")
        sys.exit(0)
    except Exception as e:
        print(f"\n\033[91m[!] 运行异常: {e}\033[0m")
        sys.exit(1)


if __name__ == "__main__":
    main()