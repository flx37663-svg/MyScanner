# -*- coding: utf-8 -*-
import argparse
import sys
import os

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
if ROOT_PATH not in sys.path:
    sys.path.insert(0, ROOT_PATH)

from core.engine import start_engine


def main():
    parser = argparse.ArgumentParser(description="MyScanner CLI")
    parser.add_argument("-u", "--url", help="目标 URL")
    parser.add_argument("-t", "--threads", type=int, help="并发线程数")
    parser.add_argument("-d", "--dir", help="报告输出目录")
    parser.add_argument("-o", "--output", help="报告文件名")
    parser.add_argument("--single", action="store_true", help="单网页模式")
    parser.add_argument("--poc", help="指定 PoC 脚本 (模糊匹配)")
    # --- 补全的参数 ---
    parser.add_argument("--depth", type=int, help="爬虫递归深度 (默认 3)")
    parser.add_argument("--pages", type=int, help="最大爬取页面数 (默认 50)")

    args = parser.parse_args()

    try:
        start_engine(args)
    except KeyboardInterrupt:
        print("\n[!] 用户中断扫描。")
    except Exception:
        import traceback
        print(f"[!] 系统异常:\n{traceback.format_exc()}")


if __name__ == "__main__":
    main()