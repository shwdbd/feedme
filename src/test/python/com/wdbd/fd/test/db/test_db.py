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
import com.wdbd.fd.common.tl as tl
import com.wdbd.fd.model.db as db
# from com.wdbd.fd.collector.server import DTServer
# from sqlalchemy import desc


# 测试数据库连接
class TestDbConnect(unittest.TestCase):

    def test_get_engine(self):
        """ 测试取得数据库引擎 """
        tl.ENVIRONMENT = 'test'
        engine = db.get_engine()
        print(engine.url)
        self.assertTrue("fd_test" in engine.url)
