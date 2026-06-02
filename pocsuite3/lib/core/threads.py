# -*- coding: utf-8 -*-
from scapy.contrib.openflow3 import cls


def run_threads(num, func, args=()):
    """ 简易仿真：直接执行任务 """
    if args:
        func(*args)
    else:
        func()