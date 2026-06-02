# -*- coding: utf-8 -*-
import argparse
import sys
import os

# 确保项目根目录在 sys.path 中
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
if ROOT_PATH not in sys.path:
    sys.path.insert(0, ROOT_PATH)

from core.engine import start_engine

def main():
    parser = argparse.ArgumentParser(description="MyScanner CLI - 企业级漏洞扫描框架")
    parser.add_argument("-u", "--url", help="目标 URL (不输入则读取 config.json)")
    parser.add_argument("-t", "--threads", type=int, help="并发线程数")
    parser.add_argument("-d", "--dir", help="指定报告输出目录 (默认为 ./reports)")
    parser.add_argument("-o", "--output", help="自定义报告文件名 (例如: struts2_scan.html)")
    parser.add_argument("--single", action="store_true", help="单网页模式 (跳过爬虫)")
    parser.add_argument("--poc", help="指定 PoC 文件名 (支持模糊匹配)")
    args = parser.parse_args()

    try:
        start_engine(args)
    except KeyboardInterrupt:
        print("\n[!] 用户中断扫描。")
    except Exception:
        import traceback
        print(f"[!] 系统运行异常:\n{traceback.format_exc()}")

if __name__ == "__main__":
    main()