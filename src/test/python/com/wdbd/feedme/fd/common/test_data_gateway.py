#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   test_tushare_gateway.py
@Time    :   2021/08/15 13:24:45
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   数据网关功能测试

'''
import unittest
import pandas as pd
from com.wdbd.feedme.fd.common.data_gateway import TushareGateWay, EFinanceGateWay
import com.wdbd.feedme.fd.common.common as tl
import efinance as ef


class TestEFinanceGateWay(unittest.TestCase):
    """ EFinance数据网关测试 """

    def setUp(self) -> None:
        tl.TEST_MODE = True
        return super().setUp()

    def test_connect(self):
        """ 测试连接API """
        gw = EFinanceGateWay()
        self.assertIsNotNone(gw)
        df = gw.call(callback=ef.stock.get_realtime_quotes)
        self.assertIsNotNone(df)
        self.assertIsInstance(df, pd.DataFrame)


# Tushare数据网关测试
class TestTushareGateway(unittest.TestCase):
    """ Tushare数据网关测试 """

    def setUp(self) -> None:
        tl.TEST_MODE = True
        return super().setUp()

    def test_connect(self):
        """ 测试连接Tusahre API """
        gw = TushareGateWay()
        self.assertIsNotNone(gw.api)

    def test_visit_data(self):
        """ 通过API访问Tushare数据 """
        sample_record = {'ts_code': '600016.SH', 'trade_date': '20180810', 'open': 5.99,
                         'high': 5.99, 'low': 5.93, 'close': 5.96, 'pre_close': 5.97, 'change': -0.01, 'pct_chg': -0.1675, 'vol': 316902.39, 'amount': 188871.924}
        # 返回Ts股票代码，dict格式
        gw = TushareGateWay()
        res = gw.call(gw.api.daily, start_date="20180810", end_date="20180811", ts_code="600016.SH", return_type="dict")
        self.assertTrue(isinstance(res, list))
        self.assertEqual(1, len(res))
        self.assertDictEqual(sample_record, res[0])

        # 返回Ts股票日线数据，dataframe格式
        gw = TushareGateWay()
        res = gw.call(gw.api.daily, start_date="20180810", end_date="20180811", ts_code="600016.SH", return_type="dataframe")
        self.assertTrue(isinstance(res, pd.core.frame.DataFrame))
        self.assertDictEqual(sample_record, res.to_dict('records')[0])

    def test_has_data(self):
        """ 测试 判断某日某交易接口是否已生成数据 """
        gw = TushareGateWay()
        self.assertTrue(gw.has_data(callback=gw.api.daily, trade_date="20221128"))   # 交易日
        self.assertFalse(gw.has_data(callback=gw.api.daily, trade_date="20221127"))   # 非交易日
        self.assertFalse(gw.has_data(callback=gw.api.daily, trade_date="19000101"))   # 肯定没有数字的日期
