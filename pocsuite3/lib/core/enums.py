# -*- coding: utf-8 -*-
class VUL_TYPE:
    SQL_INJECTION = 'SQLI'
    XSS = 'XSS'
    CODE_EXECUTION = 'RCE'
    DIR_TRAVERSAL = 'dir-traversal'
    FILE_UPLOAD = 'File Upload'
    WEAK_PASSWORD = 'PASS'
    UNAUTHORIZED_ACCESS = 'UNAUTH'

class OS:
    LINUX = "LINUX"
    WINDOWS = "WINDOWS"
    DARWIN = "DARWIN"

class OS_ARCH:
    X86 = "32bit"
    X64 = "64bit"

class ENCODER_TPYE:
    XOR = "xor"
    ALPHANUMERIC = "alphanum"