# -*- coding: utf-8 -*-

class Opt:
    def __init__(self, default='', description='', selected='', require=False):
        self.default = default
        self.description = description
        self.selected = selected
        self.require = require

# 映射所有常见的选项类
OptString = OptDict = OptItems = OptInteger = OptFloat = OptBool = Opt