# -*- coding: utf-8 -*-
from pocsuite3.api import Output, POCBase, register_poc, requests

class POC(POCBase):
    name = 'DVWA CSRF Protection Check'
    vulType = 'Cross-Site Request Forgery'

    def _verify(self):
        result = {}
        if "vulnerabilities/csrf" in self.url.lower():
            try:
                res = requests.get(self.url)
                # 判定：在修改密码的表单中，如果没有 user_token 隐藏域，则存在 CSRF 风险
                if 'password_new' in res.text and 'user_token' not in res.text:
                    result['VerifyInfo'] = {"URL": self.url, "Issue": "No CSRF Token found in form"}
                    self.set_payload("Missing user_token")
            except: pass
        return self.parse_output(result)

    def parse_output(self, result):
        output = Output(self)
        if result: output.success(result)
        else: output.fail('not vulnerable')
        return output

register_poc(POC)