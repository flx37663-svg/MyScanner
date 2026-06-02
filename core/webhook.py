# -*- coding: utf-8 -*-
import requests as raw_req
from datetime import datetime

class WebhookManager:
    def __init__(self, enabled=False, sendkey=""):
        self.enabled = enabled
        self.sendkey = sendkey
        self.api_url = f"https://sctapi.ftqq.com/{sendkey}.send" if sendkey else ""

    def send_vuln_alert(self, poc_obj, target_url, poc_file, evidence):
        if not self.enabled or not self.api_url: return
        poc_name = getattr(poc_obj, 'name', poc_file)
        vul_type = getattr(poc_obj, 'vulType', 'Vulnerability')
        now_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        title = f"🚩 漏洞发现: {poc_name}"
        description = (
            "### ⚠️ MyScanner 实时告警\n---\n"
            "**[ 漏洞基本信息 ]**\n"
            f"- **插件**: `{poc_file}`\n- **类型**: **{vul_type}**\n\n"
            "**[ 扫描目标 ]**\n"
            f"- **地址**: {target_url}\n- **时间**: {now_time}\n\n"
            "**[ Payload ]**\n"
            f"```text\n{evidence}\n```\n---\n*Powered by MyScanner Engine*"
        )
        try: raw_req.post(self.api_url, data={"title": title, "desp": description}, timeout=10)
        except: pass