#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   test_akshare.py
@Time    :   2024/03/26 15:29:31
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   针对Akshare数据源数据下载Action的功能测试
'''
import unittest
from com.wdbd.fd.services.dt.actions.akshare_action import Ak_SSE_Summary
from com.wdbd.fd.model.dt_model import ActionConfig
from com.wdbd.fd.common.tl import Result
from com.wdbd.fd.common.db_utils import DbUtils
from unittest import mock
from com.wdbd.fd.services.gateway.ak_gateway import get_ak_gateway, DataException
import akshare as ak


class Test_Ak_SSE_Summary_Old(unittest.TestCase):
    """ Akshare 市场总貌、上海证券交易所 """

    # def setUp(self) -> None:
    #     return super().setUp()

    # def test_handle(self):
    #     """ 测试下载 """
    #     config = ActionConfig()
    #     config.name = "市场总貌、上海证券交易所"

    #     action = Ak_SSE_Summary()
    #     action.set_action_parameters(config)
    #     res = action.handle()
    #     self.assertEqual(Result(), res)

    #     # TODO 检查下载后的情况
    #     self.assertEqual(3, DbUtils.count("ods_akshare_stock_sse_summary", "trade_date='20240325'"))
    #     # db_utils.clear_table
    
    def test_handle(self):
        # mock_file_path = "src/test/python/com/wdbd/fd/test/services/dt/actions/ak_test_data_files/ak_sse_summary.csv"
        
        # with mock.patch('com.wdbd.fd.services.gateway.ak_gateway.get_ak_gateway') as mocked_get_ak_gateway:
        
        #     # mocked_get_ak_gateway.return_value._instance.call.return_value = "abcde"
        #     mocked_get_ak_gateway.return_value = "abcde"
            
        #     def test_handle(self):
        mock_file_path = "src/test/python/com/wdbd/fd/test/services/dt/actions/ak_test_data_files/ak_sse_summary.csv"
        
        with mock.patch('com.wdbd.fd.services.gateway.ak_gateway.get_ak_gateway') as mocked_get_ak_gateway:
            mocked_gateway_instance = "Mock return"  # 创建一个模拟对象
            mocked_get_ak_gateway.return_value = mocked_gateway_instance  # 返回模拟对象
            
            gw = get_ak_gateway()
            print(gw)
            
            
            # mock_file = mock_open().__enter__()  # 获取mock文件对象
            # mock_file.read.return_value = "This is a test file content."
        
            # # 执行
            # config = ActionConfig()
            # config.name = "市场总貌、上海证券交易所"
            # action = Ak_SSE_Summary()
            # action.set_action_parameters(config)
            # res = action.handle()
            # self.assertEqual(Result(), res)


if __name__ == "__main__":
    unittest.main()
