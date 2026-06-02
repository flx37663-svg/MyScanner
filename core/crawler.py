# -*- coding: utf-8 -*-
import re
from urllib.parse import urljoin, urlparse, urlunparse, parse_qsl, urlencode
from pocsuite3.api import requests, logger


class Crawler:
    def __init__(self, entry_url, max_depth=3, max_pages=100):
        self.entry_url = entry_url.strip().rstrip('/')
        self.domain = urlparse(self.entry_url).netloc
        self.max_depth = max_depth  # 0 为不限制
        self.max_pages = max_pages  # 0 为不限制
        self.visited = set()
        self.discovered = set()
        self.structure_seen = set()

    def normalize_url(self, url):
        parsed = urlparse(url)
        query_params = sorted(parse_qsl(parsed.query))
        new_query = urlencode(query_params)
        return urlunparse((parsed.scheme, parsed.netloc.lower(), parsed.path, parsed.params, new_query, ''))

    def get_url_structure(self, url):
        parsed = urlparse(url)
        keys = sorted([k for k, v in parse_qsl(parsed.query)])
        return f"{parsed.netloc}{parsed.path}?{'-'.join(keys)}"

    def start(self):
        depth_info = "Unlimited" if self.max_depth == 0 else self.max_depth
        page_info = "Unlimited" if self.max_pages == 0 else self.max_pages
        logger.info(f"Crawler started (Depth: {depth_info}, Pages: {page_info})")

        todo = [(self.normalize_url(self.entry_url), 0)]
        while todo:
            # 页面总数限制逻辑
            if self.max_pages > 0 and len(self.visited) >= self.max_pages:
                logger.warn("Max pages reached, stopping crawler.")
                break

            url, depth = todo.pop(0)

            # 深度限制逻辑
            if self.max_depth > 0 and depth > self.max_depth: continue

            # 结构指纹过滤 (即使无限深度，相同结构的页面也只抓一次链接)
            struct = self.get_url_structure(url)
            if struct in self.structure_seen and depth > 0: continue

            if url in self.visited: continue
            self.visited.add(url);
            self.structure_seen.add(struct)

            try:
                res = requests.get(url, timeout=5)
                if res.status_code == 200:
                    self.discovered.add(url)
                    print(f"    [+] Link: {url} (Depth: {depth})")
                    links = re.findall(r'href=["\'](.*?)["\']', res.text)
                    forms = re.findall(r'action=["\'](.*?)["\']', res.text)
                    for raw in links + forms:
                        if any(x in raw.lower() for x in ['logout', 'javascript:', 'mailto:', '#']): continue
                        full = urljoin(url, raw)
                        if urlparse(full).netloc == self.domain:
                            norm = self.normalize_url(full)
                            if norm not in self.visited: todo.append((norm, depth + 1))
            except:
                continue

        final = [u for u in self.discovered if
                 not any(u.lower().endswith(x) for x in ['.jpg', '.png', '.css', '.js', '.pdf', '.ico'])]
        logger.success(f"Crawl complete. {len(final)} unique URLs found.")
        return final