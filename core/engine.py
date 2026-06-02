# -*- coding: utf-8 -*-
import os, sys, threading, json, importlib.util, random, string
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from core.reporter import Reporter
from core.crawler import Crawler
from core.webhook import WebhookManager

ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_PATH not in sys.path: sys.path.insert(0, ROOT_PATH)

reporter = None
webhook_inst = None
report_lock = threading.Lock();
load_lock = threading.Lock()


def load_config():
    import pocsuite3.api as api
    global webhook_inst
    path = os.path.join(ROOT_PATH, "config.json")
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                api.conf.headers, api.conf.target_url = data.get("headers", {}), data.get("target_url", "")
                api.conf.threads = data.get("threads", 5)
                api.conf.scan_settings, api.conf.report_settings = data.get("scan_settings", {}), data.get(
                    "report_settings", {})
                wb = data.get("webhook", {})
                webhook_inst = WebhookManager(wb.get("enabled"), wb.get("sendkey"))
        except Exception as e:
            print(f"[!] Config Error: {e}")


def flatten_result(res_dict):
    if not res_dict: return "N/A"
    inner = res_dict.get("Result", res_dict)
    for key in ["VerifyInfo", "ShellInfo", "DBInfo", "Stdout"]:
        if key in inner:
            v = inner[key];
            return json.dumps(v, indent=2) if isinstance(v, dict) else str(v)
    return str(inner)


def worker(poc_path, target_url):
    global reporter, webhook_inst
    poc_file = os.path.basename(poc_path)
    try:
        import pocsuite3.api as api
        api.init_thread_data()
        with load_lock:
            module_name = f"mod_{poc_file.split('.')[0]}_{random.randint(1000, 9999)}"
            spec = importlib.util.spec_from_file_location(module_name, poc_path)
            mod = importlib.util.module_from_spec(spec);
            spec.loader.exec_module(mod)
            poc_class = getattr(mod, 'POC', None) or getattr(mod, 'TestPOC', None) or getattr(mod, 'DemoPOC',
                                                                                              None) or api.CURRENT_POC_CLASS
        if poc_class:
            poc_obj = poc_class(target_url)
            poc_obj.options = {'cookie': api.conf.headers.get('Cookie', '')}
            res_obj = poc_obj._verify()
            if res_obj and getattr(res_obj, 'result', None):
                print(f"\033[92m[+] SUCCESS | {poc_file} | {target_url}\033[0m")
                evidence = flatten_result(res_obj.result)
                if webhook_inst: webhook_inst.send_vuln_alert(poc_obj, target_url, poc_file, evidence)
                with report_lock:
                    reporter.add_result(poc_file, target_url, api.thread_data.last_request,
                                        api.thread_data.last_response, evidence)
    except:
        pass


def start_engine(args):
    global reporter
    import pocsuite3.api as api
    load_config()
    target = args.url or api.conf.target_url
    threads = args.threads or api.conf.threads
    s, rs = api.conf.scan_settings, api.conf.report_settings
    if not target: return

    # 1. 发现
    urls = [target] if args.single or s.get("target_mode") == "single" else Crawler(target,
                                                                                    args.depth if args.depth is not None else s.get(
                                                                                        "max_depth", 3),
                                                                                    s.get("max_pages", 100)).start()

    # 2. 收集 PoC
    poc_dir = os.path.join(ROOT_PATH, 'pocs');
    pocs = []
    if args.poc:
        for r, d, fs in os.walk(poc_dir):
            if args.poc in fs: pocs.append(os.path.join(r, args.poc))
    else:
        for r, d, fs in os.walk(poc_dir):
            for f in fs:
                if f.endswith('.py') and not f.startswith('__'): pocs.append(os.path.join(r, f))

    if not pocs: return
    reporter = Reporter(target, len(pocs))
    print(f"[*] MyScanner Engine Active | {len(urls)} URLs x {len(pocs)} PoCs")
    with ThreadPoolExecutor(max_workers=threads) as executor:
        for u in urls:
            for p in pocs: executor.submit(worker, p, u)

    # 3. 核心修复：报告保存目录逻辑
    out_dir = args.dir or rs.get("output_dir", "./reports")
    if not os.path.exists(out_dir): os.makedirs(out_dir)

    fname = args.output or rs.get("filename", "") or f"scanner_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    full_path = os.path.join(out_dir, fname)
    reporter.generate(full_path)