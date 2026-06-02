# -*- coding: utf-8 -*-
import argparse, sys
from core.engine import start_engine

def main():
    parser = argparse.ArgumentParser(description="MyScanner CLI")
    parser.add_argument("-u", "--url", help="目标 URL")
    parser.add_argument("-t", "--threads", type=int, help="线程数")
    parser.add_argument("-d", "--dir", help="指定报告输出目录") # 新增参数
    parser.add_argument("--single", action="store_true", help="单网页模式")
    parser.add_argument("--poc", help="指定 PoC 文件")
    parser.add_argument("--depth", type=int, help="爬虫深度")
    parser.add_argument("-o", "--output", help="自定义报告文件名")
    parser.add_argument("--no-push", action="store_true", help="禁用推送")
    args = parser.parse_args()
    try: start_engine(args)
    except KeyboardInterrupt: sys.exit(0)

if __name__ == "__main__":
    main()