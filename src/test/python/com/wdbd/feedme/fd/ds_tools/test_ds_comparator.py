#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   TestDsComparator.py
@Time    :   2022/12/10 11:06:09
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   数据源内容比较器 单元测试
'''
import unittest
import com.wdbd.feedme.fd.common.common as tl
from com.wdbd.feedme.fd.orm.ods_tables import OdsTushareTradeCal, OdsAkshareTradeCal
from com.wdbd.feedme.fd.ds_tools.ds_comparator import compare_cal_ak_ts


# 交易日历
class Test_compare_cal_ak_ts(unittest.TestCase):
    """ 比较Tushare和Akshare数据源的 交易日历数据 """

    def setUp(self) -> None:
        tl.TEST_MODE = True
        session = tl.get_session()
        # Tushare
        session.query(OdsTushareTradeCal).delete()
        session.add(OdsTushareTradeCal(exchange="SSE", cal_date="20221201", is_open="1", pretrade_date=""))
        session.add(OdsTushareTradeCal(exchange="SSE", cal_date="20221202", is_open="1", pretrade_date=""))
        session.add(OdsTushareTradeCal(exchange="SSE", cal_date="20221203", is_open="1", pretrade_date=""))
        # Akshare
        session.query(OdsAkshareTradeCal).delete()
        session.add(OdsAkshareTradeCal(trade_date="20221202"))
        session.add(OdsAkshareTradeCal(trade_date="20221203"))
        session.commit()
        session.close()
        return super().setUp()

    def test_compare(self):
        """ 下载全量 """
        # 两边范围不一致
        # 交集中有1天是否交易日不一致
        res = compare_cal_ak_ts()
        self.assertIsNotNone(res)
        self.assertFalse(res["result"])
        self.assertEqual("交易日范围不同;Ts中有1个交易日在Ak中为非交易日;", res["summary"])
        m1 = "交易日范围不同。Tushare的交易日范围是['20221201', '20221203']，Akshare的交易日范围是['20221202', '20221203']"
        m2 = "日期20221201，Tushare是交易日，Akshare非交易日"
        self.assertEqual([m1, m2], res["msg"])
