# -*- coding: utf-8 -*-
class BasePOC:
    def __init__(self, url):
        self.url = url.rstrip('/')
    def verify(self):
        pass