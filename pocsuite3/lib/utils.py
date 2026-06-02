# -*- coding: utf-8 -*-
import random
import string
import re

def random_str(length=10, chars=string.ascii_letters + string.digits):
    return ''.join(random.sample(chars, length))

def get_middle_text(text, prefix, suffix):
    try:
        pattern = re.escape(prefix) + '(.*?)' + re.escape(suffix)
        return re.findall(pattern, text)[0]
    except:
        return ""

def generate_shellcode_list(**kwargs):
    return ["echo MyScanner_Test"]