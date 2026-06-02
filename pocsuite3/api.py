# -*- coding: utf-8 -*-
import threading, os, sys, logging, random, string, requests as req
from types import ModuleType

# 1. 核心 Mock 系统：解决 PoC 中各种 from pocsuite3.lib... 的报错
def _inject_internal_modules():
    targets = [
        'pocsuite3.lib.core.enums', 'pocsuite3.lib.utils',
        'pocsuite3.lib.core.data', 'pocsuite3.lib.core.interpreter_option'
    ]
    for name in targets:
        if name not in sys.modules:
            m = ModuleType(name)
            # 补全枚举
            m.OS = type('OS', (), {'LINUX': 'linux', 'WINDOWS': 'windows'})
            m.OS_ARCH = type('OS_ARCH', (), {'X86': 'x86', 'X64': 'x64'})
            # 补全工具函数
            m.random_str = lambda l=10: "".join(random.sample(string.ascii_letters, l))
            m.generate_shellcode_list = lambda **k: ["echo vulnerable"]
            sys.modules[name] = m

# 2. 补全 api 层的导出函数
def get_listener_ip(): return "127.0.0.1"
def get_listener_port(): return 4444

# 3. 配置类与流量捕获
class Conf:
    def __init__(self):
        self.headers = {}; self.timeout = 10; self.target_url = ""; self.threads = 5
        self.webhook_enabled = False; self.webhook_key = ""
        self.scan_settings = {}; self.report_settings = {}
conf = Conf()
thread_data = threading.local()
def init_thread_data(): thread_data.last_request = "N/A"; thread_data.last_response = "N/A"; thread_data.payload = "N/A"

def _capture_traffic(res):
    try:
        q = res.request
        req_headers = "\n".join([f"{k}: {v}" for k, v in q.headers.items()])
        req_body = q.body.decode('utf-8', 'ignore') if isinstance(q.body, bytes) else str(q.body or "")
        thread_data.last_request = f"{q.method} {q.url} HTTP/1.1\n{req_headers}\n\n{req_body}"
        thread_data.last_response = f"HTTP/1.1 {res.status_code}\n\n{res.text[:2000]}"
    except: pass

class RequestsProxy:
    def request(self, method, url, **kwargs):
        kwargs.setdefault('timeout', conf.timeout)
        kwargs.setdefault('headers', conf.headers)
        kwargs['verify'] = False; kwargs['allow_redirects'] = True
        res = req.request(method, url, **kwargs); _capture_traffic(res); return res
    def get(self, url, **kwargs): return self.request("GET", url, **kwargs)
    def post(self, url, **kwargs): return self.request("POST", url, **kwargs)
requests = RequestsProxy()

# 4. 基础类
class POCBase:
    def __init__(self, url=None): self.url = url; self.payload = ""; self.options = {}
    def set_payload(self, v): self.payload = v; thread_data.payload = v
    def parse_output(self, result):
        o = Output(self); return o.success(result) if result else o.fail()
    def _verify(self): return self.verify()
    def verify(self): pass

class Output:
    def __init__(self, poc=None): self.result = {}
    def success(self, r=None): self.result = r if r else True; return self
    def fail(self, msg=None): self.result = False; return self

CURRENT_POC_CLASS = None
def register_poc(p): global CURRENT_POC_CLASS; CURRENT_POC_CLASS = p
logger = type('Logger', (), {
    'info': lambda x: print(f"[*] {x}"), 'success': lambda x: print(f"\033[92m[+] {x}\033[0m"),
    'warn': lambda x: print(f"\033[93m[!] {x}\033[0m"), 'error': lambda x: print(f"\033[91m[!] {x}\033[0m")
})
VUL_TYPE = type('VUL_TYPE', (), {'CODE_EXECUTION': 'RCE', 'SQL_INJECTION': 'SQLI'})
POC_CATEGORY = type('POC_CATEGORY', (), {'EXPLOITS': type('EX', (), {'WEBAPP': 'WEB'})})

# 启动注入
_inject_internal_modules()