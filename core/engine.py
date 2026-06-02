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
                api.conf.scan_settings = data.get("scan_settings", {})
                api.conf.report_settings = data.get("report_settings", {})
                wb = data.get("webhook", {})
                webhook_inst = WebhookManager(wb.get("enabled"), wb.get("sendkey"))
        except Exception as e:
            print(f"[!] Config Error: {e}")


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
            res = poc_obj._verify()
            is_ok = bool(res.result) if (res and hasattr(res, 'result')) else bool(res)
            if is_ok:
                print(f"\033[92m[+] SUCCESS | {poc_file} | {target_url}\033[0m")
                if webhook_inst: webhook_inst.send_vuln_alert(poc_obj, target_url, poc_file)
                with report_lock:
                    reporter.add_result(poc_file, target_url, api.thread_data.last_request,
                                        api.thread_data.last_response, getattr(poc_obj, 'payload', "N/A"))
    except:
        pass


# --- core/engine.py 修改后的 start_engine 函数 ---

def start_engine(args):  # 接收 args 对象
    global reporter
    import pocsuite3.api as api
    load_config()  # 先加载配置文件作为底色

    # --- 核心：命令行参数覆盖 (CLI Overrides Config) ---
    target = args.url or api.conf.target_url
    threads = args.threads if (args.threads and args.threads > 0) else api.conf.threads

    if not target:
        print("\033[91m[!] 错误: 未指定目标 URL。使用 -u 参数或修改 config.json\033[0m")
        return

    # 提取扫描设置
    s = api.conf.scan_settings
    target_mode = "single" if args.single else s.get("target_mode", "crawler")
    max_depth = args.depth if args.depth is not None else s.get("max_depth", 3)
    max_pages = args.pages if args.pages is not None else s.get("max_pages", 100)

    # 提取 PoC 设置
    poc_mode = s.get("poc_mode", "all")
    poc_name = args.poc or s.get("poc_name", "")
    poc_group = args.group or s.get("poc_group", "")

    if args.poc: poc_mode = "single"
    if args.group: poc_mode = "group"

    # 如果指定了 --no-push，强制关闭 Webhook
    if args.no_push:
        api.conf.webhook_enabled = False

    # 1. 发现逻辑
    if target_mode == "single":
        urls = [target]
    else:
        urls = Crawler(target, max_depth=max_depth, max_pages=max_pages).start()

    # 2. PoC 加载逻辑
    poc_dir = os.path.join(ROOT_PATH, 'pocs')
    pocs = []

    if poc_mode == "single":
        p_path = os.path.join(poc_dir, poc_name)
        pocs = [p_path] if os.path.exists(p_path) else []
    elif poc_mode == "group":
        g_dir = os.path.join(poc_dir, poc_group)
        pocs = [os.path.join(g_dir, f) for f in os.listdir(g_dir) if f.endswith('.py')] if os.path.isdir(g_dir) else []
    else:
        for r, d, fs in os.walk(poc_dir):
            for f in fs:
                if f.endswith('.py') and not f.startswith('__'): pocs.append(os.path.join(r, f))

    if not pocs:
        print("\033[91m[!] 错误: 未找到可用的 PoC 脚本。\033[0m")
        return

    reporter = Reporter(target, len(pocs))
    print(f"[*] MyScanner Engine Active | {len(urls)} URLs x {len(pocs)} PoCs | Threads: {threads}")

    with ThreadPoolExecutor(max_workers=threads) as executor:
        for u in urls:
            for p in pocs: executor.submit(worker, p, u)

    # 3. 报告保存逻辑
    rep_s = api.conf.report_settings
    out_dir = rep_s.get("output_dir", "./reports")
    if not os.path.exists(out_dir): os.makedirs(out_dir)

    # 优先使用 -o 命令行参数指定的文件名
    fname = args.output or rep_s.get("filename", "") or f"scanner_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    reporter.generate(os.path.join(out_dir, fname))