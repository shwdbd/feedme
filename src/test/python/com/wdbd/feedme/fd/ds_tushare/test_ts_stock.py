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
from com.wdbd.feedme.fd.orm.ods_tables import OdsTushareTradeCal, OdsDsStat, OdsTushareStockBasic, OdsTushareDaily
from com.wdbd.feedme.fd.ds_tushare.ts_stock import TsTradeCal, TsStockList, TsStockDaily
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
        self.assertEqual(2*7, record_count)   # 7个交易所
        # 检查统计表信息
        stat = session.query(OdsDsStat).filter(OdsDsStat.ds_id == 'tushare.trade_cal').one_or_none()
        self.assertIsNotNone(stat)
        self.assertEqual(stat.ds_name, "Tushare交易日历")
        self.assertEqual(stat.start_bar, "20221120")
        self.assertEqual(stat.end_bar, "20221121")
        self.assertEqual(stat.missing_bar, "")
        self.assertEqual(stat.notes, "")
        session.close()


# A股股票清单
class TestTsStockList(unittest.TestCase):
    """ A股股票清单 数据下载 """

    def setUp(self) -> None:
        tl.TEST_MODE = True
        session = tl.get_session()
        session.query(OdsTushareStockBasic).delete()
        session.commit()
        session.close()
        return super().setUp()

    def test_download_all(self):
        """ 下载全量 """
        srv = TsStockList()
        res = srv.download()    # 下载全量数据
        self.assertDictEqual({"result": True, "msg": []}, res)

        session = tl.get_session()
        # 检查表中记录数量
        record_count = session.query(func.count(OdsTushareStockBasic.ts_code)).scalar()
        self.assertTrue(record_count > 4000)   # 股票个数4000以上
        # 检查统计表信息
        stat = session.query(OdsDsStat).filter(OdsDsStat.ds_id == 'tushare.stock_basic').one_or_none()
        self.assertIsNotNone(stat)
        self.assertEqual(stat.ds_name, "tushareA股股票基础信息")
        self.assertEqual(stat.start_bar, "")
        self.assertEqual(stat.end_bar, "")
        self.assertEqual(stat.missing_bar, "")
        self.assertEqual(stat.notes, "")
        session.close()


# A股日线
class TestTsDaily(unittest.TestCase):
    """ A股股票日线 数据下载 """

    def setUp(self) -> None:
        tl.TEST_MODE = True
        session = tl.get_session()
        session.query(OdsTushareDaily).delete()
        session.query(OdsDsStat).delete()
        session.commit()
        session.close()
        return super().setUp()

    def test_download_by_date(self):
        """ 按日下载 """
        srv = TsStockDaily()
        res = srv.download_by_date(trade_date="20221123", stock_id="600016.SH")    # 下载一个日期，一个股票日线
        self.assertDictEqual({"result": True, "msg": []}, res)

        session = tl.get_session()
        # 检查表中记录数量
        record_count = session.query(func.count(OdsTushareDaily.trade_date)).scalar()
        self.assertEqual(1, record_count)
        # 检查统计表信息
        stat = session.query(OdsDsStat).filter(OdsDsStat.ds_id == 'tushare.daily').one_or_none()
        self.assertIsNotNone(stat)
        self.assertEqual(stat.ds_name, "tushareA股日线行情（未复权）")
        self.assertEqual(stat.start_bar, "")
        self.assertEqual(stat.end_bar, "20221123")
        self.assertEqual(stat.missing_bar, "")
        self.assertEqual(stat.notes, "")
        session.close()

    # 测试全量股票下载
    def test_download_all(self):
        srv = TsStockDaily()
        srv.download_all(stockid_test="600016.SH")    # 下载一个日期，一个股票日线

        session = tl.get_session()
        # 检查一个股票的数据，记录数大于2000
        record_count = session.query(func.count(OdsTushareDaily.trade_date)).filter(OdsTushareDaily.ts_code == '600016.SH').scalar()
        self.assertTrue(record_count > 2000)
        # 检查stat表
        stat = session.query(OdsDsStat).filter(OdsDsStat.ds_id == 'tushare.daily').one_or_none()
        self.assertEqual("20001219", stat.start_bar)
        session.close()
