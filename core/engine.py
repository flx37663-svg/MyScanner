# -*- coding: utf-8 -*-
import os, sys, threading, json, importlib.util, random
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from .reporter import Reporter
from .crawler import Crawler
from .webhook import WebhookManager
from pocsuite3 import api

ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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
            module_name = f"mod_{random.randint(1000, 9999)}"
            spec = importlib.util.spec_from_file_location(module_name, poc_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            poc_class = getattr(mod, 'DemoPOC', None) or getattr(mod, 'POC', None) or getattr(mod, 'TestPOC',
                                                                                              None) or getattr(api,
                                                                                                               'CURRENT_POC_CLASS',
                                                                                                               None)

        if poc_class:
            poc_obj = poc_class(target_url)
            res_obj = poc_obj._verify()

            # --- 核心改进：双重校验 status 和 result ---
            if res_obj and getattr(res_obj, 'status', False) and getattr(res_obj, 'result', None):
                print(f"\033[92m[+] 确认漏洞 | {poc_file} | {target_url}\033[0m")
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
    if not target: return

    is_single = args.single or api.conf.scan_settings.get("target_mode") == "single"
    urls = [target] if is_single else Crawler(target, max_depth=api.conf.scan_settings.get("max_depth", 3)).start()

    poc_dir = os.path.join(ROOT_PATH, 'pocs')
    pocs = []
    for r, d, fs in os.walk(poc_dir):
        for f in fs:
            if f.endswith('.py') and not f.startswith('__'):
                if args.poc and args.poc not in f: continue
                pocs.append(os.path.join(r, f))
    if not pocs: return

    reporter = Reporter(target, len(pocs))
    print(f"[*] Engine Active | URL: {len(urls)} | PoC: {len(pocs)}")

    with ThreadPoolExecutor(max_workers=args.threads or api.conf.threads) as ex:
        for u in urls:
            for p in pocs: ex.submit(worker, p, u)

    out_dir = args.dir or api.conf.report_settings.get("output_dir", os.path.join(ROOT_PATH, "reports"))
    fname = args.output or api.conf.report_settings.get("filename",
                                                        "") or f"report_{datetime.now().strftime('%m%d_%H%M%S')}.html"
    if not os.path.exists(out_dir): os.makedirs(out_dir)
    reporter.generate(os.path.join(out_dir, fname))