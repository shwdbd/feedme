#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   test_tools.py
@Time    :   2023/06/02 16:59:06
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   工具组 单元测试
'''
import unittest
from com.wdbd.feedme.fd.siw.tools import check_rpfile_format, get_stock_info


class TestSIWTools(unittest.TestCase):

    def test_check_rpfile_format(self):
        """ 测试 检查 财报文件名 是否符合要求 """
        # 正确
        self.assertTrue(check_rpfile_format("SH600016 民生银行 2023年Q1.pdf"))
        self.assertTrue(check_rpfile_format("SH600016 民生银行 2022年年报.pdf"))
        # 错误
        self.assertFalse(check_rpfile_format("600016 xx银行 2023年Q1.pdf"))
        self.assertFalse(check_rpfile_format(
            "SH600016 民生银行 2023年Q1"))     # 无文件后缀
        self.assertFalse(check_rpfile_format(
            "600016 民生银行 2023年Q1.pdf"))   # 无交易所缩写
        self.assertFalse(check_rpfile_format(""))
        self.assertFalse(check_rpfile_format(None))

    def test_get_stock_info(self):
        """ 测试  “根据文件名，解析股票代码、期数等信息”功能 """
        # 正确
        self.assertDictEqual({
            "id": "SH600016",
            "name": "民生银行",
            "fr_date": "2023年Q1",
        }, get_stock_info("SH600016 民生银行 2023年Q1.pdf"))
        self.assertDictEqual({
            "id": "SH600016",
            "name": "民生银行",
            "fr_date": "2022年年报",
        }, get_stock_info("SH600016 民生银行 2022年年报.pdf"))
        # 错误
        self.assertIsNone(get_stock_info(""))
        self.assertIsNone(get_stock_info(None))
        self.assertIsNone(get_stock_info("xxxxxYYYYY 21.pdf"))
