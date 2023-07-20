#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   test_akshare.py
@Time    :   2023/07/13 16:28:57
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   测试Akahare数据源的数据下载
'''
import unittest
import com.wdbd.feedme.fd.common.common as tl
from com.wdbd.feedme.fd.orm.ods_tables import OdsAkshareTradeCal, OdsDsStat, OdsAkshareStock, OdsAkshareStockDaily_EM
from com.wdbd.feedme.fd.ds_akshare.ak_cal import AkTradeCal
from com.wdbd.feedme.fd.ds_akshare.ak_stock import AkCNStockList, AkStockDaily_EM
from sqlalchemy import func
from sqlalchemy.sql import and_


# 交易日历
class TestAkTradeCal(unittest.TestCase):
    """ 测试 交易日历 数据下载 """

    def setUp(self) -> None:
        tl.TEST_MODE = True
        session = tl.get_session()
        session.query(OdsAkshareTradeCal).delete()
        session.commit()
        session.close()
        return super().setUp()

    def test_download_all(self):
        """ 下载全量 """
        first_date = "19901219"
        end_date = "20231229"
        srv = AkTradeCal()
        res = srv.download()
        msg = "下载Akshare日历全量数据完毕，{0}到{1} 共8070个交易日".format(
            first_date, end_date)
        self.assertDictEqual({"result": True, "message": msg, 'data': []}, res)

        session = tl.get_session()
        # 检查表中记录数量
        record_count = session.query(func.count(
            OdsAkshareTradeCal.trade_date)).scalar()
        self.assertEqual(8070, record_count)
        # 检查 表中内容
        trade_date = session.query(OdsAkshareTradeCal.trade_date).filter(
            OdsAkshareTradeCal.trade_date == '20221216').one_or_none()
        self.assertEqual("20221216", trade_date[0])
        # 检查统计表信息
        stat = session.query(OdsDsStat).filter(
            OdsDsStat.ds_id == 'akshare.cal').one_or_none()
        self.assertIsNotNone(stat)
        self.assertEqual(stat.ds_name, "Akshare交易日历")
        self.assertEqual(stat.start_bar, first_date)
        self.assertEqual(stat.end_bar, end_date)
        self.assertEqual(stat.missing_bar, "")
        self.assertEqual(stat.notes, "")
        session.close()


# 股票清单
class TestAkStockList(unittest.TestCase):
    """ 测试 交易日历 数据下载 """

    def setUp(self) -> None:
        tl.TEST_MODE = True
        session = tl.get_session()
        session.query(OdsAkshareStock).delete()
        session.commit()
        # 添加一条历史数据
        stock = OdsAkshareStock()
        stock.stock_id = '12345.CH'
        stock.name = 'test'
        stock.exchange = 'XXX'
        session.add(stock)
        session.commit()
        session.close()
        return super().setUp()

    def test_download_all(self):
        """ 下载全量 """
        srv = AkCNStockList()
        res = srv.download()
        msg = "下载股票5476支，各交易所股票数量为：[('BJE', 210), ('SSE', 2334), ('SZE', 2931), ('XXX', 1)]"
        self.assertDictEqual({"result": True, "message": msg, 'data': []}, res)

        session = tl.get_session()
        # 检查表中记录数量
        record_count = session.query(
            func.count(OdsAkshareStock.stock_id)).scalar()
        self.assertEqual(5476, record_count)
        # 检查 表中内容
        records = session.query(OdsAkshareStock.name).filter(
            OdsAkshareStock.stock_id == '600016.SH').one_or_none()
        self.assertEqual("民生银行", records[0])
        # 检查统计表信息
        stat = session.query(OdsDsStat).filter(
            OdsDsStat.ds_id == 'akshare.cnstock_list').one_or_none()
        self.assertIsNotNone(stat)
        self.assertEqual(stat.ds_name, "AkshareA股股票清单")
        self.assertEqual(stat.start_bar, '')
        self.assertEqual(stat.end_bar, tl.today())
        self.assertEqual(stat.missing_bar, "")
        self.assertEqual(stat.notes, "")
        session.close()


# 股票日线(东方财富)
class TestAkStockDaily_EM(unittest.TestCase):
    """ 测试 股票日线(东方财富) 数据下载 """

    def setUp(self) -> None:
        tl.TEST_MODE = True
        session = tl.get_session()
        session.query(OdsAkshareStockDaily_EM).delete()
        session.commit()
        session.close()
        return super().setUp()

    def test_download_by_date(self):
        """ 按日下载 """
        trade_date = "20230719"
        srv = AkStockDaily_EM()
        res = srv.download_by_date(trade_date, test_mode=True)
        msg = "按日下载Akshare股票日线数据(日期{0}), 记录数{1}".format(trade_date, 16)
        self.assertDictEqual({"result": True, "message": msg, 'data': []}, res)

        session = tl.get_session()
        # 检查表中记录数量
        record_count = session.query(func.count(
            OdsAkshareStockDaily_EM.symbol)).scalar()
        self.assertEqual(16, record_count)
        # 检查 表中内容
        records = session.query(OdsAkshareStockDaily_EM).filter(and_(
            OdsAkshareStockDaily_EM.symbol == '000001.SZ', OdsAkshareStockDaily_EM.trade_date == trade_date)).one_or_none()
        self.assertEqual(11.23, records.p_open)
        # 检查统计表信息
        stat = session.query(OdsDsStat).filter(
            OdsDsStat.ds_id == 'akshare.cnstock_daily_em').one_or_none()
        self.assertIsNotNone(stat)
        self.assertEqual(stat.ds_name, "AkshareA股日线 东财")
        # self.assertEqual(stat.start_bar, '')
        # self.assertEqual(stat.end_bar, trade_date)
        # self.assertEqual(stat.missing_bar, "")
        # self.assertEqual(stat.notes, "")
        session.close()

    def test_download_by_stock(self):
        """ 按股下载 """
        trade_date = "20230710"
        stock_id = '600016.SH'
        srv = AkStockDaily_EM()
        res = srv.download_by_stock(stock_id, start_date=trade_date, end_date='20230719')
        msg = "按股下载Akshare股票日线数据(代码：{0}), 更新记录{1}条".format(stock_id, 8)
        self.assertDictEqual({"result": True, "message": msg, 'data': []}, res)

        session = tl.get_session()
        # # 检查表中记录数量
        record_count = session.query(func.count(
            OdsAkshareStockDaily_EM.symbol)).scalar()
        self.assertEqual(8, record_count)
        # 检查 表中内容
        records = session.query(OdsAkshareStockDaily_EM).filter(and_(
            OdsAkshareStockDaily_EM.symbol == '600016.SH', OdsAkshareStockDaily_EM.trade_date == '20230710')).one_or_none()
        self.assertEqual(3.77, records.p_open)
        # 检查统计表信息
        stat = session.query(OdsDsStat).filter(
            OdsDsStat.ds_id == 'akshare.cnstock_daily_em').one_or_none()
        self.assertIsNotNone(stat)
        self.assertEqual(stat.ds_name, "AkshareA股日线 东财")
        # self.assertEqual(stat.start_bar, '')
        # self.assertEqual(stat.end_bar, trade_date)
        # self.assertEqual(stat.missing_bar, "")
        # self.assertEqual(stat.notes, "")
        session.close()


# TODO 测试日线数据全量下载

# TODO 测试日线数据增量下载

# TODO 测试日历缺失数据查询

# TODO 测试日线缺失数据查询

# TODO 测试股票清单全量下载


if __name__ == "__main__":
    pass
