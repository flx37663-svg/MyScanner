# -*- coding: utf-8 -*-
import re, requests
from urllib.parse import urljoin, urlparse, urlunparse, parse_qsl, urlencode

class Crawler:
    def __init__(self, entry_url, max_depth=3, max_pages=50, headers=None):
        self.entry_url = entry_url.strip().rstrip('/')
        self.domain = urlparse(self.entry_url).netloc
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.headers = headers or {}
        self.visited = set()
        self.discovered = set()

    def normalize(self, url):
        try:
            p = urlparse(url)
            path = p.path.split(';')[0]
            # 保留原有的参数排序逻辑，防止重复抓取
            query = urlencode(sorted(parse_qsl(p.query)))
            return urlunparse((p.scheme, p.netloc.lower(), path, '', query, ''))
        except:
            return url

    def is_static(self, url):
        # 原有静态资源过滤逻辑
        exts = ['.jpg', '.jpeg', '.png', '.gif', '.css', '.js', '.woff', '.ttf', '.pdf', '.ico', '.zip', '.svg', '.mp4']
        return any(urlparse(url).path.lower().endswith(e) for e in exts)

    def start(self):
        todo = [(self.normalize(self.entry_url), 0)]
        while todo and len(self.discovered) < self.max_pages:
            url, depth = todo.pop(0)
            if url in self.visited or depth > self.max_depth:
                continue
            self.visited.add(url)
            if urlparse(url).netloc != self.domain or self.is_static(url):
                continue

            try:
                self.discovered.add(url)
                print(f"    [*] Found URL: {url}")
                if len(self.discovered) >= self.max_pages: break

                # 发起请求时带上配置中的 Headers (如 Cookie)
                res = requests.get(url, timeout=5, verify=False, allow_redirects=True, headers=self.headers)
                if res.status_code == 200:
                    # 原有 href/action 正则提取
                    links = re.findall(r'(?:href|action)=["\'](.*?)["\']', res.text)
                    for r in links:
                        # 防注销过滤
                        if any(x in r.lower() for x in ['javascript:', 'mailto:', '#', 'logout', 'exit', 'signout']): continue
                        norm = self.normalize(urljoin(url, r))
                        if urlparse(norm).netloc == self.domain and norm not in self.visited:
                            todo.append((norm, depth + 1))
            except:
                continue
        return list(self.discovered)