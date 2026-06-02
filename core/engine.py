# -*- coding: utf-8 -*-
import os, sys, threading, json, importlib.util, random
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from .reporter import Reporter
from .crawler import Crawler
from .webhook import WebhookManager
from pocsuite3 import api

ROOT_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
reporter = None;
webhook_inst = None
report_lock = threading.Lock();
load_lock = threading.Lock()


def load_config():
    global webhook_inst
    path = os.path.join(ROOT_PATH, "config.json")
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                api.conf.headers = data.get("headers", {})
                api.conf.target_url = data.get("target_url", "")
                api.conf.threads = data.get("threads", 5)
                api.conf.scan_settings = data.get("scan_settings", {})
                api.conf.report_settings = data.get("report_settings", {})
                wb = data.get("webhook", {})
                webhook_inst = WebhookManager(wb.get("enabled"), wb.get("sendkey"))
        except:
            pass


def worker(poc_path, target_url):
    global reporter, webhook_inst
    poc_file = os.path.basename(poc_path)
    try:
        api.init_thread_data()
        with load_lock:
            m_name = f"mod_{random.randint(1000, 9999)}"
            spec = importlib.util.spec_from_file_location(m_name, poc_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            poc_class = getattr(mod, 'DemoPOC', None) or getattr(mod, 'POC', None) or getattr(mod, 'TestPOC',
                                                                                              None) or getattr(api,
                                                                                                               'CURRENT_POC_CLASS',
                                                                                                               None)

        if poc_class:
            poc_obj = poc_class(target_url)
            res_obj = poc_obj._verify()
            if res_obj and getattr(res_obj, 'status', False) and getattr(res_obj, 'result', None):
                print(f"\033[92m[+] SUCCESS | {poc_file} | {target_url}\033[0m")
                evidence = json.dumps(res_obj.result, indent=2)
                if webhook_inst: webhook_inst.send_vuln_alert(poc_obj, target_url, poc_file, evidence)
                with report_lock:
                    reporter.add_result(poc_file, target_url, api.thread_data.last_request,
                                        api.thread_data.last_response, evidence)
    except:
        pass


def start_engine(args):
    global reporter
    load_config()
    target = args.url or api.conf.target_url
    if not target:
        print("[!] 未指定目标。");
        return

    is_single = args.single or api.conf.scan_settings.get("target_mode") == "single"

    if is_single:
        urls = [target]
    else:
        # --- 核心修复：优先级 命令行 > 配置文件 > 默认值 ---
        s = api.conf.scan_settings
        c_depth = args.depth if args.depth is not None else s.get("max_depth", 3)
        c_pages = args.pages if args.pages is not None else s.get("max_pages", 50)

        print(f"[*] 启动爬虫 | 深度: {c_depth} | 最大页面: {c_pages}")
        urls = Crawler(target, max_depth=c_depth, max_pages=c_pages).start()

    poc_dir = os.path.join(ROOT_PATH, 'pocs')
    pocs = []
    for r, d, fs in os.walk(poc_dir):
        for f in fs:
            if f.endswith('.py') and not f.startswith('__'):
                if args.poc and args.poc not in f: continue
                pocs.append(os.path.join(r, f))
    if not pocs: return

    reporter = Reporter(target, len(pocs))
    print(f"[*] 扫描开始 | URL总数: {len(urls)} | PoC总数: {len(pocs)} | 线程: {args.threads or api.conf.threads}")

    with ThreadPoolExecutor(max_workers=args.threads or api.conf.threads) as ex:
        for u in urls:
            for p in pocs: ex.submit(worker, p, u)

    # 处理输出
    out_dir = args.dir or api.conf.report_settings.get("output_dir", os.path.join(ROOT_PATH, "reports"))
    fname = args.output or api.conf.report_