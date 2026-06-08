# MyScanner - 轻量化自动化漏洞扫描框架

![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

MyScanner 是一款功能完备、高度模块化的轻量级漏洞扫描工具。它旨在为安全从业者提供一个简洁且强大的自动化扫描平台。通过内置的 `pocsuite3` API 仿真层，MyScanner 可以直接利用大量现有的专业 PoC 脚本对目标进行深度安全检测。

## 🌟 核心特性

*   **智能 Session 感知爬虫**：支持携带自定义请求头（Cookie），解决授权状态下（如登录后的 DVWA）的深度爬取难题，内置防注销逻辑。
*   **高兼容性 PoC 引擎**：
    *   **pocsuite3 仿真层**：完美模拟官方 API，支持 `POC_CATEGORY`、`VUL_TYPE` 等元数据。
    *   **变量防错注入**：自动在脚本加载时注入 `cmd_result` 与 `result` 变量，消除第三方脚本编写不规范导致的报错。
*   **灵活的多模式扫描**：
    *   支持 **All**（全量）、**Group**（目录分组）、**Single**（单脚本模糊匹配）三种 PoC 加载模式。
    *   支持 **Crawler**（自动爬取）与 **Single Page**（单页检测）两种目标发现模式。
*   **可视化 HTML 报告**：生成交互式 Bootstrap 报告，完整记录每个漏洞触发时的原始 **HTTP 请求包** 与 **响应内容**。
*   **实时 Webhook 告警**：集成“Server酱”接口，发现漏洞后第一时间推送到微信或手机端。
*   **多配置管理**：支持通过命令行开关快速切换不同的配置文件。

---

## 📂 项目结构

```text
├── core/
│   ├── base.py         # PoC 基础类
│   ├── crawler.py      # 智能爬虫模块 (支持正则、归一化、Headers)
│   ├── engine.py       # 调度引擎 (多线程管理、PoC 动态加载、锁机制)
│   ├── reporter.py     # 可视化 HTML 报告生成模块
│   └── webhook.py      # Server酱告警通知模块
├── pocs/               # PoC 脚本仓库（支持按子目录分组）
├── reports/            # 扫描报告输出目录
├── api.py              # pocsuite3 API 仿真层 (Shim)
├── main.py             # 程序入口命令行工具
├── config.json         # 默认配置文件
└── requirements.txt    # 依赖库列表
```
---
**🚀 快速上手**

### 1. 环境准备
```bash
# 下载项目
git clone https://github.com/your-username/MyScanner.git
cd MyScanner

# 安装基础依赖 (requests 为核心依赖)
pip install requests
```
---
### 2. 配置文件说明 (默认使用config.json)
```json
{
  "target_url": "http://127.0.0.1:8080",
  "headers": {
    "Cookie": "PHPSESSID=xxx; security=low",
    "User-Agent": "MyScanner/1.0"
  },
  "scan_settings": {
    "target_mode": "crawler",
    "poc_mode": "group",
    "poc_group": "dvwa_poc"
  },
  "report_settings": {
    "output_dir": "./reports",
    "filename": "test.html"
  }
}
```
---
### 3. 运行扫描

**使用默认配置启动：**
```bash
python main.py
```

**指定特定配置文件：**
```bash
python main.py -c dev_env.json
```

**命令行覆盖配置进行测试：**
```bash
# 指定目标、线程数，并模糊匹配含有 "sqli" 的 PoC 进行扫描
python main.py -u http://example.com -t 15 --poc sqli
```
---
### ⌨️ 命令行参数汇总

| 参数          | 缩写   | 功能说明                    |
|:------------|:-----|:------------------------|
| `--help`    | `-h` | 扫描器使用说明                 |
| `--config`  | `-c` | 指定自定义配置文件路径             |
| `--url`     | `-u` | 覆盖配置文件中的目标 URL          |
| `--threads` | `-t` | 设置并发线程数                 |
| `--poc`     | 无    | 模糊匹配 PoC 文件名进行单点测试      |
| `--single`  | 无    | 单页模式：禁用爬虫，仅对当前 URL 进行检测 |
| `--depth`   | 无    | 爬虫递归深度 (默认 3)           |
| `--pages`   | 无    | 最大爬取页面数 (默认 50)         |
| `--dir`     | `-d` | 报告输出目录 (默认 ./reports)   |
| `--output`  | `-o` | 报告文件名 (默认 test.html)    |
---

## 🔌 PoC 插件系统

MyScanner 的核心威力来自于其高度灵活的 PoC 插件系统。它支持动态加载符合 `pocsuite3` 标准的脚本。

### 1. PoC 组织结构
您可以根据漏洞类型、目标组件或项目需求，在 `pocs/` 目录下自由创建子目录：
```text
pocs/
├── dvwa_poc/          # 用于配置 "poc_group": "dvwa_poc"
│   ├── sqli.py
│   └── xss.py
├── struts2/           # 用于配置 "poc_group": "struts2"
│   ├── s2_045.py
│   └── s2_048.py
└── common_check.py    # 通用检测脚本
```
### 2. 插件编写标准
扫描器内置了仿真 API，PoC 脚本只需继承 POCBase 并实现 _verify 或 verify 方法即可。

**基础模版示例 (pocs/demo_vuln.py)：**
```python
from pocsuite3.api import POCBase, Output, register_poc, requests, VUL_TYPE
class DemoPOC(POCBase):
    name = '漏洞名称示例'
    vulType = VUL_TYPE.CODE_EXECUTION  # 漏洞类型
    desc = '这里填写漏洞的详细描述'

    def _check(self):
        """核心检测逻辑"""
        result = {}
        # 使用框架内置的带流量捕获功能的 requests
        res = requests.get(self.url + "/test_vuln.php")
        if "vulnerable_flag" in res.text:
            result['VerifyInfo'] = {"URL": self.url, "Payload": "/test_vuln.php"}
            return result
        return False

    def _verify(self):
        """验证模式"""
        return self.parse_output(self._check())

register_poc(DemoPOC)
```
---

## 📢 实时告警 (Webhook)

MyScanner 集成了基于 **Server酱 (FTQQ)** 的实时告警功能。当扫描引擎在后台发现高危漏洞时，会立即通过 Webhook 将详细信息推送到您的手机（微信/PushDeer/邮件等）。

### 1. 功能配置
在 `config.json` 中配置您的推送密钥：
```json
"webhook": {
  "enabled": true,
  "sendkey": "SCTxxxxxxxxx..." // 在 https://sct.ftqq.com 获取您的 SendKey
}
```
### 2. 推送内容预览
🚀 快速上手
1. 环境准备
```bash
# 下载项目
git clone https://github.com/your-username/MyScanner.git
cd MyScanner

# 安装基础依赖
pip install requests 
```
**告警信息包含：漏洞名称、漏洞类型、目标地址、Payload 证据及发现时间。**
---
# ⚠️ 免责声明

注意： 本工具仅用于合法授权的企业安全评估、漏洞研究及教学演示。
请勿将其用于未经授权的渗透测试。
使用者在利用本工具进行扫描时产生的任何法律责任，由使用者本人承担。
框架本身不包含攻击性 Payload，所有检测结果均基于您放入 pocs/ 文件夹下的脚本内容。
