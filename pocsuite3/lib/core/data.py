# -*- coding: utf-8 -*-
import os
from pocsuite3.api import logger, conf

# 模拟知识库对象
kb = type('KB', (), {'targets': set(), 'results': []})()

class Paths:
    def __init__(self):
        # 爆破脚本会引用这个路径，指向根目录的字典
        self.WEAK_PASS = os.path.join(os.getcwd(), "pass.txt")
        self.DATA_PATH = os.getcwd()

paths = Paths()