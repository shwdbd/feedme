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
from com.wdbd.fd.services.gateway.ak_gateway import get_ak_gateway, AkshareGateWay
import akshare as ak
from com.wdbd.fd.services.gateway import DataException


class TestAKGateway(unittest.TestCase):
    """ 测试Akshare书记员网关 """

    def test_get_ak_gateway(self):
        """ 测试取得网关对象 """
        gw = get_ak_gateway()
        self.assertIsInstance(gw, AkshareGateWay)
        # # 测试 Mock状态下
        # gw = get_ak_gateway(mode="Mock")
        # self.assertIsInstance(gw, AkGatewayMock)

    def test_standardize_symbol(self):
        """ 测试 股票id 格式转换 """
        gw = get_ak_gateway()
        self.assertEqual("600016", gw._standardize_symbol("600016.SH"))
        self.assertEqual("600016", gw._standardize_symbol("600016"))
 
    def test_standardize_symbol_with_dot(self):
        gw = get_ak_gateway()
        # 假设有一个带有'.'的资产ID
        symbol_with_dot = "ABC.DEF"
        # 调用_standardize_symbol方法
        standardized_symbol = gw._standardize_symbol(symbol_with_dot)
        # 断言返回的结果是我们期望的，即'.'之前的部分
        self.assertEqual(standardized_symbol, "ABC")

    def test_standardize_symbol_without_dot(self):
        gw = get_ak_gateway()
        # 假设有一个不带'.'的资产ID
        symbol_without_dot = "ABC"
        # 调用_standardize_symbol方法
        standardized_symbol = gw._standardize_symbol(symbol_without_dot)
        # 断言返回的结果与输入相同，因为没有'.'需要处理
        self.assertEqual(standardized_symbol, "ABC")

    def test_standardize_symbol_with_multiple_dots(self):
        gw = get_ak_gateway()
        # 假设有一个带有多个'.'的资产ID
        symbol_with_multiple_dots = "ABC.DEF.GHI"
        # 调用_standardize_symbol方法，预期只取到第一个'.'之前的部分
        standardized_symbol = gw._standardize_symbol(symbol_with_multiple_dots)
        # 断言返回的结果是我们期望的，即第一个'.'之前的部分
        self.assertEqual(standardized_symbol, "ABC")

    def test_standardize_symbol_empty_string(self):
        gw = get_ak_gateway()
        # 假设资产ID是一个空字符串
        empty_symbol = ""
        # 调用_standardize_symbol方法
        standardized_symbol = gw._standardize_symbol(empty_symbol)
        # 断言返回的结果与输入相同，因为没有'.'需要处理
        self.assertEqual(standardized_symbol, "")

    def test_call(self):
        """ 测试调取数据源API功能 """
        gw = get_ak_gateway()
        self.assertIsInstance(gw, AkshareGateWay)
        # 调用
        df = gw.call(callback=ak.stock_sse_summary)
        self.assertIsNotNone(df)
        self.assertListEqual(['项目', '股票', '主板', '科创板'], df.columns.tolist())

        # 测试, 使用 600016.SH 样式
        df = gw.call(callback=ak.stock_zh_a_hist, symbol="600016.SH", start_date="20240225", end_date="20240228")
        self.assertIsNotNone(df)

        # 测试, api调用失败的情况
        try:
            df = gw.call(callback=ak.stock_zh_a_hist, symbol="aaaaaaa", start_date="20240225", end_date="20240228")
            self.fail()
        except DataException as de:
            self.assertIsInstance(de, DataException)


class TestGetAkGateway(unittest.TestCase):

    def test_get_ak_gateway_normal(self):
        """
        测试正常情况下的get_ak_gateway方法, 确保返回的是AkshareGateWay对象实例。
        """
        ak_gateway = get_ak_gateway()
        self.assertTrue(isinstance(ak_gateway, AkshareGateWay))

    def test_get_ak_gateway_singleton(self):
        """
        测试get_ak_gateway方法的单例模式, 确保多次调用返回的是同一个AkshareGateWay对象实例。
        """
        ak_gateway1 = get_ak_gateway()
        ak_gateway2 = get_ak_gateway()
        self.assertTrue(ak_gateway1 is ak_gateway2)


if __name__ == "__main__":
    unittest.main()
    # print("aaa")
