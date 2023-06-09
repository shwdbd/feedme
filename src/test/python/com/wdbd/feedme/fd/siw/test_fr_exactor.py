#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   test_fr_exactor.py
@Time    :   2023/06/05 22:13:19
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   测试 财报读取器
'''
import unittest
from com.wdbd.feedme.fd.siw import FinanceReportExactor


class TestFrExactor(unittest.TestCase):
    """ 测试财报读取器功能 """

    def test_load_by_file(self):
        file_name = 'C:/Users/wang/OneDrive/3_Work/GTP01 A股财报/SH600016 民生银行 2022年年报.pdf'
        srv = FinanceReportExactor()
        res = srv.load_by_file(file_name)
        self.assertIsNotNone(res)
        self.assertTrue(res["result"])
        self.assertEqual("", res["message"])
        self.assertIsNotNone(res["stock"])
        self.assertEqual("SH600016", res["stock"]["id"])
        self.assertEqual("民生银行", res["stock"]["name"])
        self.assertEqual("2022年年报", res["stock"]["fr_date"])
        # TODO 股票指标
        self.assertIsNotNone(res["index"])
