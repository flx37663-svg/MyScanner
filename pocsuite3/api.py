# -*- coding: utf-8 -*-
import threading, os, sys, random, string, builtins
import requests as req
from types import ModuleType


def _inject_internal_modules():
    setattr(builtins, 'cmd_result', "");
    setattr(builtins, 'result', {})

    class Exploits:
        WEBAPP = 'Web'; NETWORK = 'Net'

    class Category:
        EXPLOITS = Exploits

    class VulType:
        CODE_EXECUTION = 'RCE';
        SQL_INJECTION = 'SQLI'
        CROSS_SITE_SCRIPTING = 'XSS';
        REMOTE_COMMAND_EXECUTION = 'RCE'
        REMOTE_CODE_EXECUTION = 'RCE';
        ARBITRARY_FILE_READ = 'FileRead'

    targets = ['pocsuite3.lib.core.enums', 'pocsuite3.lib.utils', 'pocsuite3.lib.core.data',
               'pocsuite3.lib.core.interpreter_option']

    class BaseOption:
        def __init__(self, default, *args, **kwargs): self.default = default

    for name in targets:
        if name not in sys.modules:
            m = ModuleType(name)
            m.OptString = m.OptDict = m.OptInt = m.OptBool = m.OptFloat = BaseOption
            m.VUL_TYPE = VulType;
            m.POC_CATEGORY = Category
            m.random_str = lambda l=10, *args, **kwargs: "".join(random.sample(string.ascii_letters, l))
            sys.modules[name] = m
    return Category, VulType


class Conf:
    def __init__(self):
        self.headers = {};
        self.timeout = 10;
        self.target_url = "";
        self.threads = 5
        self.scan_settings = {};
        self.report_settings = {}


conf = Conf();
thread_data = threading.local()


def init_thread_data(): thread_data.last_request = "N/A"; thread_data.last_response = "N/A"


class RequestsProxy:
    def request(self, method, url, **kwargs):
        kwargs.setdefault('timeout', conf.timeout);
        kwargs.setdefault('headers', conf.headers)
        kwargs['verify'] = False
        try:
            res = req.request(method, url, **kwargs)
            # 全流量捕获逻辑
            q = res.request
            h = "\n".join([f"{k}: {v}" for k, v in q.headers.items()])
            b = q.body.decode('utf-8', 'ignore') if isinstance(q.body, bytes) else str(q.body or "")
            thread_data.last_request = f"{q.method} {q.url} HTTP/1.1\n{h}\n\n{b}"
            thread_data.last_response = f"HTTP/1.1 {res.status_code}\n\n{res.text[:1000]}"
            return res
        except:
            return type('MockRes', (), {'text': '', 'status_code': 0, 'headers': {}, 'url': url})

    def get(self, url, **kwargs):
        return self.request("GET", url, **kwargs)

    def post(self, url, **kwargs):
        return self.request("POST", url, **kwargs)


requests = RequestsProxy()


class Output:
    def __init__(self, poc=None): self.result = {}; self.status = False

    def success(self, r=None):
        if r: self.result = r; self.status = True
        return self

    def fail(self, msg=""): self.status = False; return self


class POCBase:
    def __init__(self, url=None):
        self.url = url; self.options = {}

    def get_option(self, key):
        opts = self._options() if hasattr(self, '_options') else {}
        return opts.get(key).default if key in opts else ""

    def parse_output(self, result):
        o = Output(self)
        return o.success(result) if result else o.fail()

    def _verify(self):
        try:
            for func in ['_check', 'verify', '_verify']:
                if hasattr(self, func) and func != '_verify':
                    res = getattr(self, func)()
                    if isinstance(res, Output): return res
                    return self.parse_output(res)
        except:
            pass
        return Output(self).fail()


POC_CATEGORY, VUL_TYPE = _inject_internal_modules()
register_poc = lambda p: setattr(sys.modules[__name__], 'CURRENT_POC_CLASS', p)
logger = type('Logger', (), {'info': print, 'success': lambda x: print(f"[+] {x}"), 'error': print, 'warn': print})