# -*- coding: utf-8 -*-
import os, sys, threading, json, importlib.util, random
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


def load_config(custom_path=None):
    global webhook_inst
    path = custom_path if (custom_path and os.path.exists(custom_path)) else os.path.join(ROOT_PATH, "config.json")
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
            # 解决 cmd_result 报错的注入
            mod.cmd_result = "";
            mod.result = {}
            spec.loader.exec_module(mod)
            poc_class = getattr(mod, 'DemoPOC', None) or getattr(mod, 'POC', None) or \
                        getattr(mod, 'TestPOC', None) or getattr(api, 'CURRENT_POC_CLASS', None)

        if poc_class:
            poc_obj = poc_class(target_url)
            res_obj = poc_obj._verify()
            if res_obj and getattr(res_obj, 'status', False):
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
    load_config(args.config)  # 支持自定义配置
    target = args.url or api.conf.target_url
    if not target: print("[!] 未指定目标。"); return

    is_single = args.single or api.conf.scan_settings.get("target_mode") == "single"
    if is_single:
        urls = [target]
    else:
        s = api.conf.scan_settings
        c_depth = args.depth if args.depth is not None else s.get("max_depth", 3)
        c_pages = args.pages if args.pages is not None else s.get("max_pages", 50)
        print(f"[*] 启动爬虫 | 深度: {c_depth} | 最大页面: {c_pages}")
        urls = Crawler(target, max_depth=c_depth, max_pages=c_pages, headers=api.conf.headers).start()

    # 完善的多模式 PoC 筛选
    poc_dir = os.path.join(ROOT_PATH, 'pocs')
    pocs = []
    s_conf = api.conf.scan_settings
    mode = s_conf.get("poc_mode", "all")
    for r, d, fs in os.walk(poc_dir):
        for f in fs:
            if f.endswith('.py') and not f.startswith('__'):
                if args.poc:  # 命令行模糊匹配
                    if args.poc not in f: continue
                elif mode == "group" and s_conf.get("poc_group") not in r:
                    continue
                elif mode == "single" and s_conf.get("poc_name") and s_conf.get("poc_name") not in f:
                    continue
                pocs.append(os.path.join(r, f))

    if not pocs: return
    reporter = Reporter(target, len(pocs))
    t_count = args.threads or api.conf.threads
    print(f"[*] 扫描开始 | URL总数: {len(urls)} | PoC总数: {len(pocs)} | 线程: {t_count}")

    with ThreadPoolExecutor(max_workers=t_count) as ex:
        for u in urls:
            for p in pocs: ex.submit(worker, p, u)

    r_conf = api.conf.report_settings
    out_dir = args.dir or r_conf.get("output_dir", os.path.join(ROOT_PATH, "reports"))
    if not os.path.exists(out_dir): os.makedirs(out_dir)
    fname = args.output or r_conf.get("filename", "report")
    if not fname.endswith(".html"): fname += ".html"
    reporter.generate(os.path.join(out_dir, fname))
    print(f"[*] 扫描任务结束。")