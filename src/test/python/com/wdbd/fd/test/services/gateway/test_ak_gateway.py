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
from unittest.mock import MagicMock, Mock, patch
import requests
import socket


class TestAKGateway(unittest.TestCase):
    """ 测试Akshare书记员网关 """

    def test_get_ak_gateway(self):
        """ 测试取得网关对象 """
        gw = get_ak_gateway()
        self.assertIsInstance(gw, AkshareGateWay)

    def test_call(self):
        """ 测试调取数据源API功能 """        
        # 使用Mock对象模拟get_ak_gateway函数
        def mock_get_ak_gateway():
            mock_gw = Mock(spec=AkshareGateWay)
            mock_gw.call.side_effect = [
                # 第一个调用返回一个模拟的DataFrame
                Mock(columns=['项目', '股票', '主板', '科创板']),
                # 第二个调用返回一个模拟的DataFrame
                Mock(),
                # 第三个调用抛出一个DataException
                DataException("API调用失败")
            ]
            return mock_gw

        # 在测试期间替换实际的get_ak_gateway函数
        with patch('com.wdbd.fd.services.gateway.ak_gateway.get_ak_gateway', mock_get_ak_gateway):  # 需要导入patch
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
                self.fail("Expected an DataException to be raised")
            except DataException as de:
                self.assertIsInstance(de, DataException)

    def test_check_connection_success(self):
        # 模拟网络请求成功
        with patch('com.wdbd.fd.services.gateway.ak_gateway.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response

            gw = AkshareGateWay()
            assert gw.check_connection() is True

    def test_check_connection_failure(self):
        # 模拟网络请求失败
        with patch('com.wdbd.fd.services.gateway.ak_gateway.requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.RequestException()

            gw = AkshareGateWay()
            assert gw.check_connection() is False

    def test_check_connection_timeout(self):
        # 模拟网络请求超时
        with patch('com.wdbd.fd.services.gateway.ak_gateway.requests.get') as mock_get:
            mock_get.side_effect = socket.timeout()
            
            gw = AkshareGateWay()
            assert gw.check_connection() is False


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


class TestAKGateway_Standardize(unittest.TestCase):
    """ 测试Akshare网关 格式化功能 """

    def setUp(self):
        self.gateway = AkshareGateWay()

    def test_standardize_symbol_with_dot(self):
        # 测试symbol中含有点的情况
        symbol = "600016.SH"
        expected = "600016"
        standardized = self.gateway._standardize_symbol(symbol)
        self.assertEqual(standardized, expected, f"Failed for symbol: {symbol}")

    def test_standardize_symbol_without_dot(self):
        # 测试symbol中不含有点的情况
        symbol = "600016"
        expected = "600016"
        standardized = self.gateway._standardize_symbol(symbol)
        self.assertEqual(standardized, expected, f"Failed for symbol: {symbol}")

    def test_standardize_symbol_with_invalid_format(self):
        # 测试symbol格式不正确的情况
        symbol = "SH600016"
        expected = "SH600016"
        standardized = self.gateway._standardize_symbol(symbol)
        self.assertEqual(standardized, expected, f"Failed for symbol: {symbol}")


if __name__ == "__main__":
    unittest.main()

    # # 创建测试套件
    # suite = unittest.TestSuite()
    # # 将特定的测试用例添加到套件中
    # suite.addTest(TestAKGateway_Standardize('test_standardize_symbol_with_dot'))
    # # 使用测试套件运行测试
    # runner = unittest.TextTestRunner()
    # runner.run(suite)
