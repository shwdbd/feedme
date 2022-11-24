#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   test_ts_stock.py
@Time    :   2022/11/24 06:55:39
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   针对股票类数据下载的测试
'''
import unittest
import com.wdbd.feedme.fd.common.common as tl
from com.wdbd.feedme.fd.orm.ods_tables import OdsTushareTradeCal, OdsDsStat
from com.wdbd.feedme.fd.ds_tushare.ts_stock import TsTradeCal
from sqlalchemy import func


# 交易日历
class TestTsTradeCal(unittest.TestCase):
    """ 交易日历 数据下载 """

    def setUp(self) -> None:
        tl.TEST_MODE = True
        session = tl.get_session()
        session.query(OdsTushareTradeCal).delete()
        session.commit()
        session.close()
        return super().setUp()

    def test_download_all(self):
        """ 下载全量 """
        srv = TsTradeCal()
        res = srv.download_all(start_date="20221120", end_date="20221121")  # 仅2天数据
        self.assertDictEqual({"result": True, "msg": []}, res)

        session = tl.get_session()
        # 检查表中记录数量
        record_count = session.query(func.count(OdsTushareTradeCal.cal_date)).scalar()
        self.assertEqual(2*5, record_count)   # 目前只有5个交易所数据
        # 检查统计表信息
        stat = session.query(OdsDsStat).filter(OdsDsStat.ds_id == 'tushare.trade_cal').one_or_none()
        self.assertIsNotNone(stat)
        self.assertEqual(stat.ds_name, "Tushare交易日历")
        self.assertEqual(stat.start_bar, "20221120")
        self.assertEqual(stat.end_bar, "20221121")
        self.assertEqual(stat.missing_bar, "")
        self.assertEqual(stat.notes, "")
        session.close()
