# -*- coding: utf-8 -*-
import threading, os, sys, random, string, builtins
import requests as req
from types import ModuleType


def _inject_internal_modules():
    # 注入安全变量作为保底
    setattr(builtins, 'cmd_result', "")
    setattr(builtins, 'result', {})

    targets = ['pocsuite3.lib.core.enums', 'pocsuite3.lib.utils',
               'pocsuite3.lib.core.data', 'pocsuite3.lib.core.interpreter_option']

    class BaseOption:
        def __init__(self, default, *args, **kwargs): self.default = default

    for name in targets:
        if name not in sys.modules:
            m = ModuleType(name)
            m.OptString = m.OptDict = m.OptInt = m.OptBool = m.OptFloat = BaseOption
            m.VUL_TYPE = type('VUL_TYPE', (), {'CODE_EXECUTION': 'RCE', 'SQL_INJECTION': 'SQLI'})
            m.POC_CATEGORY = type('POC_CATEGORY', (), {'EXPLOITS': type('EX', (), {'WEBAPP': 'WEB'})})
            m.random_str = lambda l=10, *args, **kwargs: "".join(random.sample(string.ascii_letters, l))
            sys.modules[name] = m


class Conf:
    def __init__(self):
        self.headers = {};
        self.timeout = 10;
        self.target_url = "";
        self.threads = 5
        self.scan_settings = {};
        self.report_settings = {}


conf = Conf()
thread_data = threading.local()


def init_thread_data(): thread_data.last_request = "N/A"; thread_data.last_response = "N/A"


class RequestsProxy:
    def request(self, method, url, **kwargs):
        kwargs.setdefault('timeout', conf.timeout);
        kwargs.setdefault('headers', conf.headers);
        kwargs['verify'] = False
        try:
            res = req.request(method, url, **kwargs)
            # 记录流量
            q = res.request
            h = "\n".join([f"{k}: {v}" for k, v in q.headers.items()])
            b = q.body.decode('utf-8', 'ignore') if isinstance(q.body, bytes) else str(q.body or "")
            thread_data.last_request = f"{q.method} {q.url} HTTP/1.1\n{h}\n\n{b}"
            thread_data.last_response = f"HTTP/1.1 {res.status_code}\n\n{res.text[:1000]}"
            return res
        except:
            return type('MockRes', (), {'text': '', 'content': b'', 'status_code': 0, 'headers': {}})

    def get(self, url, **kwargs):
        return self.request("GET", url, **kwargs)

    def post(self, url, **kwargs):
        return self.request("POST", url, **kwargs)


requests = RequestsProxy()


class Output:
    def __init__(self, poc=None):
        self.result = {}
        self.status = False  # 核心：显式状态位

    def success(self, r=None):
        # 只有传入了非空字典或真值，才标记为扫描成功
        if r and (not isinstance(r, dict) or len(r) > 0):
            self.result = r
            self.status = True
        return self

    def fail(self):
        self.status = False
        return self


class POCBase:
    def __init__(self, url=None):
        self.url = url; self.options = {}

    def get_option(self, key):
        opts = self._options() if hasattr(self, '_options') else {}
        return opts.get(key).default if key in opts else ""

    def parse_output(self, result):
        o = Output(self)
        # 只有 result 包含具体信息（如 VerifyInfo）时才通过
        if result:
            return o.success(result)
        return o.fail()

    def _verify(self):
        try:
            if hasattr(self, '_check'): return self._check()
            if hasattr(self, 'verify'): return self.verify()
        except:
            return Output(self).fail()
        return Output(self).fail()


register_poc = lambda p: setattr(sys.modules[__name__], 'CURRENT_POC_CLASS', p)
logger = type('Logger', (), {'info': print, 'success': lambda x: print(f"[+] {x}"), 'error': print, 'warn': print})
VUL_TYPE = type('VUL_TYPE', (), {'CODE_EXECUTION': 'RCE', 'SQL_INJECTION': 'SQLI'})
POC_CATEGORY = type('POC_CATEGORY', (), {'EXPLOITS': type('EX', (), {'WEBAPP': 'WEB'})})
_inject_internal_modules()