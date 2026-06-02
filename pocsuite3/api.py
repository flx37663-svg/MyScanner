# -*- coding: utf-8 -*-
import threading, os, sys, logging, random, string
import requests as req
from types import ModuleType

logging.getLogger("urllib3").setLevel(logging.CRITICAL)

if 'telnetlib' not in sys.modules:
    mock_tn = ModuleType('telnetlib')
    class MockT:
        def __init__(self, *args, **kwargs): pass
        def open(self, *args, **kwargs): pass
        def read_until(self, *args, **kwargs): return b""
        def write(self, *args, **kwargs): pass
        def expect(self, *args, **kwargs): return (0, None, b"")
        def close(self): pass
    mock_tn.Telnet = MockT
    sys.modules['telnetlib'] = mock_tn

class Conf:
    def __init__(self):
        self.headers = {}; self.timeout = 10; self.target_url = ""; self.threads = 5
        self.webhook_enabled = False; self.webhook_key = ""
        self.scan_settings = {}; self.report_settings = {}
conf = Conf()
thread_data = threading.local()

def init_thread_data():
    thread_data.last_request = "N/A"; thread_data.last_response = "N/A"; thread_data.payload = "N/A"

def cookie_to_dict(cookie_str):
    cookies = {}
    if not cookie_str or not isinstance(cookie_str, str): return cookies
    for line in cookie_str.split(';'):
        if '=' in line:
            k, v = line.strip().split('=', 1); cookies[k] = v
    return cookies

def _capture_traffic(res):
    try:
        q = res.request
        h_str = "\n".join([f"{k}: {v}" for k, v in q.headers.items()])
        b_raw = q.body if q.body else ""
        b_str = b_raw.decode('utf-8', 'ignore') if isinstance(b_raw, bytes) else str(b_raw)
        thread_data.last_request = f"{q.method} {q.url} HTTP/1.1\n{h_str}\n\n{b_str}"
        res_h = "\n".join([f"{k}: {v}" for k, v in res.headers.items()])
        thread_data.last_response = f"HTTP/1.1 {res.status_code}\n{res_h}\n\n{res.text[:2000]}"
    except: pass

class RequestsProxy:
    def request(self, method, url, **kwargs):
        c = conf.headers.get('Cookie', '')
        if 'cookies' not in kwargs and c: kwargs['cookies'] = cookie_to_dict(c)
        h = kwargs.get('headers', {})
        h.setdefault('User-Agent', conf.headers.get('User-Agent', 'Scanner/1.0'))
        kwargs['headers'] = h; kwargs.setdefault('timeout', conf.timeout)
        kwargs['verify'] = False; kwargs['allow_redirects'] = True
        res = req.request(method, url, **kwargs); _capture_traffic(res); return res
    def get(self, url, **kwargs): return self.request("GET", url, **kwargs)
    def post(self, url, **kwargs): return self.request("POST", url, **kwargs)

requests = RequestsProxy()
class VUL_TYPE: SQL_INJECTION='SQLI'; XSS='XSS'; CODE_EXECUTION='RCE'; DIR_TRAVERSAL='dir-traversal'; FILE_UPLOAD='File Upload'; WEAK_PASSWORD='PASS'
class POCBase:
    def __init__(self, url=None):
        self.url = url or conf.target_url; self.payload = ""; self.options = {}
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