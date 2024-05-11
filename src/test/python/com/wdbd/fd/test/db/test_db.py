#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   test_db.py
@Time    :   2023/12/20 10:47:49
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   测试数据库功能
'''
import unittest
from com.wdbd.fd.common import tl
from com.wdbd.fd.model.db import get_engine


# 测试数据库连接
class TestDbConnect(unittest.TestCase):
    """ 数据库连接测试 """


    def test_get_engine(self):
        """ 测试取得数据库引擎 """
        tl.ENVIRONMENT = 'test'
        engine = get_engine()
        # print(engine.url)
        self.assertTrue("fd_test" in engine.url)
