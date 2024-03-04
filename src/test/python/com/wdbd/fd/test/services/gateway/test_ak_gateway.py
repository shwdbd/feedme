#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   test_ak_gateway.py
@Time    :   2024/02/28 16:34:29
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   测试Akshare数据网关
'''
import unittest
from com.wdbd.fd.services.gateway.ak_gateway import get_ak_gateway, AkshareGateWay, AkGatewayMock
import akshare as ak
from com.wdbd.fd.services.gateway import DataException


class TestAKGateway(unittest.TestCase):
    """ 测试Akshare书记员网关 """

    def test_get_ak_gateway(self):
        """ 测试取得网关对象 """
        gw = get_ak_gateway()
        self.assertIsInstance(gw, AkshareGateWay)
        # 测试 Mock状态下
        gw = get_ak_gateway(mode="Mock")
        self.assertIsInstance(gw, AkGatewayMock)

    def test_standardize_symbol(self):
        """ 测试 股票id 格式转换 """
        gw = get_ak_gateway()
        self.assertEqual("600016", gw._standardize_symbol("600016.SH"))
        self.assertEqual("600016", gw._standardize_symbol("600016"))

    def test_call(self):
        """ 测试调取数据源API功能 """
        gw = get_ak_gateway()
        self.assertIsInstance(gw, AkshareGateWay)
        # 调用
        df = gw.call(callback=ak.stock_sse_summary)
        self.assertIsNotNone(df)
        self.assertListEqual(['项目', '股票', '主板', '科创板'], df.columns.tolist())

        # 测试，使用 600016.SH 样式
        df = gw.call(callback=ak.stock_zh_a_hist, symbol="600016.SH", start_date="20240225", end_date="20240228")
        self.assertIsNotNone(df)

        # 测试，api调用失败的情况
        try:
            df = gw.call(callback=ak.stock_zh_a_hist, symbol="aaaaaaa", start_date="20240225", end_date="20240228")
            self.fail()
        except DataException as de:
            self.assertIsInstance(de, DataException)
