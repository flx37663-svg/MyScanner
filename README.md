# MyScanner 🚀
**全自动 Web 漏洞扫描框架 (Automated Web Scanner)**

MyScanner 是一款高度模块化、全自动化的漏洞扫描引擎。它实现了从“入口发现 -> 自动爬取 -> 插件匹配 -> 认证探测 -> 实时告警 -> 专业报告”的完整工业级闭环流程。

---

## ⚙️ 配置文件全解析 (config.json)

`config.json` 是系统的核心大脑。以下是每一个字段的详细功能说明：

### 1. 基础连接配置
- **target_url**: 扫描的起始地址（入口点）。
- **threads**: 并发线程数。建议 5-20。线程越多速度越快，但目标服务器压力越大。
- **timeout**: 单个 HTTP 请求的超时时间（秒）。
- **headers**: 全局注入的请求头。
    - **Cookie**: 存放认证信息（如 PHPSESSID），这是实现全自动认证扫描的关键。
    - **User-Agent**: 模拟浏览器指纹，防止被简单策略拦截。

### 2. 扫描模式设置 (scan_settings)
- **target_mode**: 
    - `crawler`: 开启全自动深度爬虫。
    - `single`: 禁用爬虫，仅探测 target_url 指定的单一页面。
- **poc_mode**:
    - `all`: 运行 pocs/ 目录下所有的漏洞插件。
    - `single`: 仅运行特定的单一插件（配合 poc_name 使用）。
    - `group`: 运行特定的插件组（配合 poc_group 使用）。
- **poc_name**: 仅在 `single` 模式下生效，填入文件名（如 `sqli.py`）。
- **poc_group**: 仅在 `group` 模式下生效，填入 pocs 目录下的子文件夹名。
- **max_depth**: 爬虫递归层级。`0` 代表不限制，`1` 代表只爬首页，推荐值为 `3`。
- **max_pages**: 爬取页面总数上限。`0` 代表不限制。防止在无限链接陷阱中死循环。

### 3. 报告与保存 (report_settings)
- **output_dir**: 报告存放的物理路径（默认为 `./reports`）。
- **filename**: 报告保存的文件名。留空则系统按 `scanner_年月日_时分秒.html` 自动命名。

### 4. 实时告警推送 (webhook)
- **enabled**: 是否开启个人微信实时推送 (true/false)。
- **sendkey**: 从 sct.ftqq.com (Server酱) 获取的唯一 SCT 密钥。

---

## 🛠️ 典型扫描场景配置全集 (Best Practices)

下表展示了如何通过组合 `config.json` 中的参数，来应对不同的渗透测试任务：

| 扫描目标与需求场景 | target_mode | poc_mode | 关键辅助参数 | 场景描述 |
| :--- | :--- | :--- | :--- | :--- |
| **全量资产深度体检** | `crawler` | `all` | `max_depth: 3` | 从首页开始，递归三层挖掘所有页面并运行所有插件。 |
| **单点漏洞复现/回测** | `single` | `single` | `poc_name: "sqli.py"` | 已知某个 URL 有漏洞，仅用指定的 PoC 进行快速验证。 |
| **专项漏洞组深度扫描** | `crawler` | `group` | `poc_group: "cms_vuls"` | 对全站进行爬取，但只运行 `pocs/cms_vuls/` 目录下的脚本。 |
| **全站搜索特定 CVE** | `crawler` | `single` | `poc_name: "cve-2024-xxx.py"` | 某种高危漏洞爆发，全自动在全站范围内寻找该漏洞。 |
| **高并发接口压力探测** | `single` | `all` | `threads: 50` | 针对单一入口运行所有插件，并开启极高线程（慎用）。 |
| **无限深度“钻取”模式** | `crawler` | `all` | `max_depth: 0` | 不限爬取深度，直到翻遍网站每一个角落。建议配合 `max_pages` 使用。 |
| **轻量级快速巡检** | `crawler` | `all` | `max_depth: 1` | 仅扫描首页以及首页能直接点进的一级链接，速度极快。 |
| **静默/离线安全扫描** | `any` | `any` | `"enabled": false` | 禁用 Webhook 微信推送，结果仅保存在本地 reports 目录。 |
| **自定义归档扫描** | `any` | `any` | `filename: "project_A.html"` | 指定固定文件名，方便将扫描结果整合进特定的项目报告。 |

---

## 💡 配置小贴士 (Pro Tips)

1.  **关于线程 (`threads`)**：如果目标是 Windows 上的 XAMPP 或旧版 IIS，线程建议不要超过 10，否则可能触发 Web 服务器的并发限制。
2.  **关于深度 (`max_depth`)**：设置超过 5 层可能会导致扫描时间指数级增加。对于一般 Web 应用，3 层深度通常足以覆盖所有核心逻辑。
3.  **关于路径 (`output_dir`)**：如果你在 Docker 或云服务器中运行，可以将 `output_dir` 指向一个 Web 目录，这样你就可以通过浏览器直接在线远程查看 HTML 报告。
---

## 🚀 快速上手

1. **环境初始化**: 执行 `python settings.py`。
2. **配置认证**: 编辑 `config.json` 填入目标 URL 和最新的 Cookie。
3. **启动扫描**: 执行 `python main.py`。

---

## 📝 命令行覆盖参数 (CLI)

可以通过命令行实时覆盖配置文件中的选项，无需修改 JSON：
- `-u, --url`: 覆盖目标地址。
- `-t, --threads`: 指定线程数。
- `--single`: 强制单网页模式。
- `--poc`: 指定单个 PoC 文件运行。
- `--group`: 运行指定的插件文件夹。
- `--depth`: 设置最大爬取深度。
- `-o, --output`: 自定义保存的文件名。
- `--no-push`: 此次运行不发送微信提醒。

---


## 📝 插件 (PoC) 开发标准
git add .
MyScanner 兼容标准化的 Pocsuite3 编写格式，建议统一使用 `_verify()` 作为探测方法：

```python
from pocsuite3.api import POCBase, Output, register_poc, requests

class POC(POCBase):
    def _verify(self):
        result = {}
        # 探测逻辑，框架会自动处理 Cookie 和流量记录
        res = requests.get(self.url, params={'id': "1'"})
        if "sql syntax" in res.text.lower():
            result['VerifyInfo'] = {"URL": self.url, "Payload": "1'"}
            self.set_payload("1'") 
        return self.parse_output(result)

    def parse_output(self, result):
        output = Output(self)
        if result: output.success(result)
        else: output.fail()
        return output

register_poc(POC)
```

---

## ⚠️ 免责声明
本工具仅供持有合法授权的安全审计、教学研究及企业自查使用。因非法使用、未授权扫描导致的法律责任及后果，由使用者本人承担。