#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   test_fdapi_akshare.py
@Time    :   2023/08/02 13:11:44
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   针对fd api的Akshare实现的单元测试
'''
import unittest
from com.wdbd.feedme.fd.fd_api import get_dates


class TestFdApi_get_dates(unittest.TestCase):
    
    def test_get_dates(self):
        """ 如果收尾日期不存在，则抛出异常，如20220231 """
        dates = get_dates(start="20220228", end="20220231")
        self.assertListEqual(['20220228'], dates)
        
        # 错误的end日期
        # self.assertRaises(Exception, get_dates, ['20220228', False, '20220231'])
        self.assertRaises(ValueError, get_dates(start="20220228", end="20220231", is_trade_date_only=False))
        
        # self.assertRaises(get_dates(start="20220228", end="20220231", is_trade_date_only=False))
        # with 
        
        # try:
        #     dates = get_dates(start="20220228", end="20220231", is_trade_date_only=False)
        #     self.fail()
        # except:
        #     pass
