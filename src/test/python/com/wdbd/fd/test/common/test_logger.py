#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   test_logger.py
@Time    :   2023/12/19 14:35:18
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   日志功能单元测试
'''
import unittest
from com.wdbd.fd.common.tl import get_logger, get_server_logger, get_action_logger


class TestFdLogger(unittest.TestCase):

    def test_logger(self):
        self.assertIsNotNone(get_logger())
        self.assertIsNotNone(get_server_logger())
        self.assertIsNotNone(get_action_logger("我的Action"))
