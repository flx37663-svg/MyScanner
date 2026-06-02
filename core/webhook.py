# -*- coding: utf-8 -*-
import requests as raw_req
from datetime import datetime

class WebhookManager:
    def __init__(self, enabled=False, sendkey=""):
        self.enabled = enabled; self.sendkey = sendkey
        self.api_url = f"https://sctapi.ftqq.com/{sendkey}.send" if sendkey else ""

    def send_vuln_alert(self, poc_obj, target_url, poc_file):
        if not self.enabled or not self.api_url: return
        poc_name = getattr(poc_obj, 'name', poc_file)
        vul_type = getattr(poc_obj, 'vulType', 'Exploit')
        payload = getattr(poc_obj, 'payload', 'N/A')
        title = f"🚩 漏洞发现: {poc_name}"
        desc = (
            "### ⚠️ Scanner 实时告警\n---\n"
            f"**[ 漏洞信息 ]**\n- **插件**: `{poc_file}`\n- **类型**: **{vul_type}**\n\n"
            f"**[ 目标 ]**\n- **地址**: {target_url}\n- **时间**: {datetime.now().strftime('%H:%M:%S')}\n\n"
            f"**[ 证据 ]**\n```text\n{payload}\n```\n---\n*Pocsuite-Lite Engine*"
        )
        try: raw_req.post(self.api_url, data={"title": title, "desp": desc}, timeout=10)
        except: pass