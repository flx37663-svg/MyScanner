# -*- coding: utf-8 -*-
import os, html
from datetime import datetime

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8"><title>Scanner Report</title>
    <link href="https://cdn.bootcdn.net/ajax/libs/twitter-bootstrap/5.3.0/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: #f5f7fa; font-size: 13px; font-family: sans-serif; }
        .navbar { background: #1a2a3a; color: white; padding: 10px 20px; font-weight: bold; }
        .vuln-item { background: white; border: 1px solid #ddd; margin-bottom: 5px; cursor: pointer; }
        .vuln-detail { display: none; padding: 20px; background: #fafafa; border-top: 1px solid #eee; }
        pre { background: #2b2b2b; color: #f8f8f2; padding: 15px; border-radius: 5px; white-space: pre-wrap; word-break: break-all; font-family: monospace; }
        .payload-box { background: #fef0f0; color: #f56c6c; padding: 10px; border: 1px solid #fde2e2; border-radius: 4px; margin-bottom: 10px; font-family: monospace; }
    </style>
</head>
<body>
    <div class="navbar">SCANNER | Professional Vulnerability Report</div>
    <div class="container mt-4">
        <div class="alert alert-dark">Target: {{ target }} | Found: {{ vuln_count }} | Time: {{ gen_time }}</div>
        <div id="results-list">{{ rows_html }}</div>
    </div>
    <script>function toggleDetail(id){var e=document.getElementById('detail-'+id);e.style.display=(e.style.display==='block')?'none':'block';}</script>
</body>
</html>
"""

class Reporter:
    def __init__(self, target, total_pocs):
        self.target = target
        self.results = []
    def add_result(self, n, u, q, r, p):
        self.results.append({
            "name": n, "url": u,
            "req": html.escape(str(q)),
            "res": html.escape(str(r)),
            "payload": html.escape(str(p)),
            "time": datetime.now().strftime("%H:%M:%S")
        })
    def generate(self, filename):
        rows = ""
        for i, item in enumerate(self.results):
            rows += f"""
            <div class="vuln-item">
                <div class="p-3 d-flex" onclick="toggleDetail({i})">
                    <div style="flex:1"><b>{item['url']}</b></div>
                    <div class="badge bg-danger">{item['name']}</div>
                </div>
                <div id="detail-{i}" class="vuln-detail">
                    <b>Evidence:</b><div class="payload-box">{item['payload']}</div>
                    <b>HTTP Request:</b><pre>{item['req']}</pre>
                    <b>HTTP Response (Preview):</b><pre>{item['res']}</pre>
                </div>
            </div>"""
        content = HTML_TEMPLATE.replace("{{ target }}", self.target).replace("{{ vuln_count }}", str(len(self.results))).replace("{{ gen_time }}", datetime.now().strftime("%Y-%m-%d %H:%M:%S")).replace("{{ rows_html }}", rows)
        with open(filename, "w", encoding="utf-8") as f: f.write(content)
        print(f"[*] Report saved: {os.path.abspath(filename)}")