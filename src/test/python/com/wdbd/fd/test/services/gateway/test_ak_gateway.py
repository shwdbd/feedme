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
import socket
from unittest.mock import MagicMock, Mock, patch
import requests
import akshare as ak
from com.wdbd.fd.services.gateway.ak_gateway import get_ak_gateway, AkshareGateWay
from com.wdbd.fd.services.gateway import DataException


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
            df = gw.call(callback=ak.stock_zh_a_hist
                        , symbol="600016.SH", start_date="20240225", end_date="20240228")
            self.assertIsNotNone(df)

            # 测试, api调用失败的情况
            try:
                df = gw.call(callback=ak.stock_zh_a_hist
                            , symbol="aaaaaaa", start_date="20240225", end_date="20240228")
                self.fail("Expected an DataException to be raised")
            except DataException as de:
                self.assertIsInstance(de, DataException)

    def test_check_connection_success(self):
        """ 模拟网络请求成功 """
        with patch('com.wdbd.fd.services.gateway.ak_gateway.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response

            gw = AkshareGateWay()
            assert gw.check_connection() is True

    def test_check_connection_failure(self):
        """ 模拟网络请求失败 """
        with patch('com.wdbd.fd.services.gateway.ak_gateway.requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.RequestException()

            gw = AkshareGateWay()
            assert gw.check_connection() is False

    def test_check_connection_timeout(self):
        """ 模拟网络请求超时 """
        with patch('com.wdbd.fd.services.gateway.ak_gateway.requests.get') as mock_get:
            mock_get.side_effect = socket.timeout()
            gw = AkshareGateWay()
            assert gw.check_connection() is False

    def test_symbol_exchange_2_tscode(self):
        """ 测试symbol_exchange_2_tscode方法 """
        akgw = get_ak_gateway()
        result = akgw.symbol_exchange_2_tscode("600016", "SH")
        assert result == "600016.SH", result

        result = akgw.symbol_exchange_2_tscode("600016", "SZ")
        assert result == "600016.SZ", result

        result = akgw.symbol_exchange_2_tscode("600016", "XX")
        assert result == "600016.XX", result

        # 错误的股票代码，返回原值
        result = akgw.symbol_exchange_2_tscode("60001A", "SH")
        assert result == "60001A", result

        result = akgw.symbol_exchange_2_tscode("60001A", "XX")
        assert result == "60001A", result

        result = akgw.symbol_exchange_2_tscode("00700", "HK")   # 长度不够
        assert result == "00700", result

        result = akgw.symbol_exchange_2_tscode("", "HK")
        assert result == "", result

        result = akgw.symbol_exchange_2_tscode("", "")
        assert result == "", result

        result = akgw.symbol_exchange_2_tscode("600016.SH", "SH")
        assert result == "600016.SH", result

        # 错误的输入参数
        result = akgw.symbol_exchange_2_tscode(unittest.mock.MagicMock(), "SH")
        self.assertIsInstance(result, unittest.mock.MagicMock)


class TestGetAkGateway(unittest.TestCase):
    """ 测试get_ak_gateway函数 """

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


class TestAKGatewayStandardize(unittest.TestCase):
    """ 测试Akshare网关 格式化功能 """

    def setUp(self):
        self.gateway = AkshareGateWay()

    def test_standardize_symbol_with_dot(self):
        """ 测试symbol中含有点的情况 """
        symbol = "600016.SH"
        expected = "600016"
        standardized = self.gateway.standardize_symbol(symbol)
        self.assertEqual(standardized, expected, f"Failed for symbol: {symbol}")

    def test_standardize_symbol_without_dot(self):
        """ 测试symbol中不含有点的情况 """
        symbol = "600016"
        expected = "600016"
        standardized = self.gateway.standardize_symbol(symbol)
        self.assertEqual(standardized, expected, f"Failed for symbol: {symbol}")

    def test_standardize_symbol_with_invalid_format(self):
        """ 测试symbol格式不正确的情况 """
        symbol = "SH600016"
        expected = "SH600016"
        standardized = self.gateway.standardize_symbol(symbol)
        self.assertEqual(standardized, expected, f"Failed for symbol: {symbol}")


class TestAKGatewayJudgeStockExchange(unittest.TestCase):
    """ 测试 根据A股股票代码判断其所属的交易所和板块 """

    def setUp(self) -> None:
        self.gw = get_ak_gateway()
        return super().setUp()

    def test_valid_shanghai_stock(self):
        """ 测试上海证券交易所主板股票 """
        self.assertEqual(self.gw.judge_stock_exchange('600000'), ('SH', '主板'))

    def test_valid_shanghai_tech_board_stock(self):
        """ 测试上海证券交易所科创板股票 """
        self.assertEqual(self.gw.judge_stock_exchange('688000'), ('SH', '科创板'))

    def test_valid_shenzhen_main_board_stock(self):
        """ 测试深圳证券交易所主板/中小板股票 """
        self.assertEqual(self.gw.judge_stock_exchange('000001'), ('SZ', '主板/中小板'))

    def test_valid_shenzhen_chi_next_stock(self):
        """ 测试深圳证券交易所创业板股票 """
        self.assertEqual(self.gw.judge_stock_exchange('300001'), ('SZ', '创业板'))

    def test_valid_beijing_old_third_board_stock(self):
        """ 测试北京证券交易所老三板股票 """
        self.assertEqual(self.gw.judge_stock_exchange('400001'), ('BJ', '老三板'))

    def test_valid_beijing_new_third_board_stock(self):
        """ 测试北京证券交易所新三板股票 """
        self.assertEqual(self.gw.judge_stock_exchange('430001'), ('BJ', '新三板'))
        self.assertEqual(self.gw.judge_stock_exchange('830001'), ('BJ', '新三板'))

    def test_invalid_stock_code_length(self):
        """ 测试股票代码长度不足6位的无效情况 """
        self.assertEqual(self.gw.judge_stock_exchange('600'), ('无效的股票代码', ''))

    def test_invalid_stock_code_format(self):
        """ 测试股票代码格式错误的无效情况 """
        self.assertEqual(self.gw.judge_stock_exchange('600A00'), ('无效的股票代码', ''))

    def test_invalid_stock_code_non_numeric(self):
        """ 测试股票代码包含非数字字符的无效情况 """
        self.assertEqual(self.gw.judge_stock_exchange('60000A'), ('无效的股票代码', ''))


if __name__ == "__main__":
    unittest.main()

    # # 创建测试套件
    # suite = unittest.TestSuite()
    # # 将特定的测试用例添加到套件中
    # suite.addTest(TestAKGateway_Standardize('test_standardize_symbol_with_dot'))
    # # 使用测试套件运行测试
    # runner = unittest.TextTestRunner()
    # runner.run(suite)
