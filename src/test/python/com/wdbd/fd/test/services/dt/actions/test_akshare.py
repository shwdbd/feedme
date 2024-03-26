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


class Test_Ak_SSE_Summary(unittest.TestCase):
    """ Akshare 市场总貌、上海证券交易所 """

    def test_handle(self):
        """ 测试下载 """
        config = ActionConfig()
        config.name = "市场总貌、上海证券交易所"

        action = Ak_SSE_Summary()
        action.set_action_parameters(config)
        res = action.handle()
        self.assertEqual(Result(), res)
        
        # TODO 检查下载后的情况
        # TODO db_utils 工具函数：count
        # db_utils.clear_table
