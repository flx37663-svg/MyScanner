# -*- coding: utf-8 -*-
import argparse, sys, os
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
if ROOT_PATH not in sys.path: sys.path.insert(0, ROOT_PATH)
from core.engine import start_engine

def main():
    parser = argparse.ArgumentParser(description="MyScanner CLI")
    parser.add_argument("-c", "--config", help="指定配置文件")
    parser.add_argument("-u", "--url", help="目标 URL")
    parser.add_argument("-t", "--threads", type=int, help="线程数")
    parser.add_argument("-d", "--dir", help="报告目录")
    parser.add_argument("-o", "--output", help="文件名")
    parser.add_argument("--single", action="store_true", help="单页模式")
    parser.add_argument("--poc", help="PoC模糊匹配")
    parser.add_argument("--depth", type=int, help="爬虫深度")
    parser.add_argument("--pages", type=int, help="最大页面")

    args = parser.parse_args()
    try: start_engine(args)
    except KeyboardInterrupt: print("\n[!] 用户中断。")
    except Exception:
        import traceback
        print(f"[!] 异常:\n{traceback.format_exc()}")

if __name__ == "__main__": main()